#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import platform
import csv
from pathlib import Path

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests import Session, HTTPError
from tqdm import tqdm

from .constants import API_BASE, MG_ANALYSES_BASE_URL, MG_ANALYSES_DOWNLOADS_URL
from .exceptions import FailToGetException

logger = logging.getLogger(__name__)


def bulk_download(args):
    """List of program arguments."""

    logging.info("Running bulk download now...")

    project_id = args.accession
    output_path = args.output_path
    version = args.pipeline
    result_group = args.result_group

    program = BulkDownloader(project_id, output_path, version, result_group)
    program.run()
    logging.info("Program finished.")


class BulkDownloader:
    """
    Helper tool allowing to download result data for the specified project
    accession.
    """

    # Set of files, which should be ignored for amplicon datasets
    non_amplicon_file_labels = {
        "Predicted CDS with annotation",
        "Predicted CDS without annotation",
        "Processed reads with annotation",
        "Processed reads without annotation",
        "Predicted ORF without annotation",
        "Processed reads with pCDS",
    }

    def __init__(self, project_id, output_path, version, result_group):
        self.project_id = project_id
        self.output_path = output_path
        self.version = version
        self.result_group = result_group
        self._init_program()
        self.headers = {
            "Accept": "application/json",
        }
        # http session
        retry_strategy = Retry(
            total=3, status_forcelist=[500, 502, 503, 504], backoff_factor=1
        )
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        http = Session()
        http.mount(MG_ANALYSES_BASE_URL, retry_adapter)
        self.http = http

    def _init_program(self):

        if not self.output_path:
            self.output_path = os.getcwd()

        # Print out the program settings
        self._print_program_settings()

    def _print_program_settings(self):
        logging.info("Running the program with the following setting...")
        logging.info("Project: %s" % self.project_id)

        logging.info(
            "Pipeline version: %s" % self.version
            if self.version
            else "Pipeline version: " "Not specified"
        )
        logging.info(
            "Result group: %s" % self.result_group
            if self.result_group
            else "Result group: Not specified"
        )
        logging.info("API_BASE: %s" % API_BASE)
        logging.info("Output directory: %s" % self.output_path)
        logging.debug("Python version: " + platform.python_version())

    def download_resource_by_url(self, url, output_file_name):
        """
        Kicks off a download and stores the file at the given path.

        :param url: Resource location.
        :param output_file_name: Path of the output file.
        :return:
        """
        output_file_name_tmp = output_file_name + ".tmp"

        logging.debug("Starting the download of the following file...")
        logging.debug(url)
        logging.debug("Saving file in:\n" + output_file_name_tmp)

        try:
            with self.http.get(url) as response:
                response.raise_for_status()
                with open(output_file_name_tmp, "wb") as f:
                    f.write(response.content)
        except HTTPError as http_error:
            logging.error(http_error)
            raise
        except IOError as io_error:
            logging.error(io_error)
            raise
        logging.debug("Download finished.")
        # move to final destination
        try:
            os.rename(output_file_name_tmp, output_file_name)
        except FileExistsError:
            logger.error("File %s exists. Over-writing." % output_file_name)
            os.remove(output_file_name)
            os.rename(output_file_name_tmp, output_file_name)

    def download_file(
        self,
        download_group_type_key,
        description_label,
        experiment_type,
        pipeline_version,
        result_group,
        file_name,
        download_url,
        dest_dir,
        project_id,
    ):
        """Download file from MGnify API.
        If the file exists it won't downloaded again but there is no
        integrity check.
        """
        subdir_folder_name = download_group_type_key.lower().replace(" ", "_")

        # TODO: Remove the following if case if EMG-742 is resolved
        if (
            experiment_type == "amplicon"
            and description_label in self.non_amplicon_file_labels
        ):
            return
            # TODO: Remove the following if case if EMG-741 is resolved
        elif description_label == "Phylogenetic tree" and pipeline_version == "2.0":
            return
        if result_group and result_group != subdir_folder_name:
            return

        sub_dir = Path(
            os.path.join(dest_dir, project_id, pipeline_version, subdir_folder_name)
        )

        logging.debug("Creating path: " + str(sub_dir))

        sub_dir.mkdir(parents=True, exist_ok=True)

        output_file_name = os.path.join(str(sub_dir), file_name)

        if os.path.exists(output_file_name):
            logger.debug("File %s exists. Skipping." % output_file_name)
            return
        try:
            self.download_resource_by_url(download_url, output_file_name)
        except (IOError, HTTPError) as e:
            logger.error("File download file error. Skipping.")
            logger.error(e)

    def run(self):
        """Get a project using MGnify RESTful API."""

        project_id = self.project_id

        params = {
            "study_accession": project_id,
        }

        logging.debug("Obtaining the data for project %s" % project_id)

        if self.version:
            params["pipeline_version"] = self.version

        logging.debug("Requesting url %s" % MG_ANALYSES_BASE_URL)

        response = self.http.get(
            MG_ANALYSES_BASE_URL, params=params, headers=self.headers
        )

        if not response.ok:
            logger.error("Failed to get the project %s from the API" % project_id)
            logger.error("Error: %s" % response.status_code)
            return

        response_data = response.json()

        num_results = response_data["meta"]["pagination"]["count"]

        logging.debug("Total results %s" % num_results)

        num_results_processed = 0
        total_results_processed = 0

        with tqdm(total=num_results) as progress_bar:

            while total_results_processed < num_results:

                num_results_processed = self.process_page(response_data, progress_bar)
                total_results_processed += num_results_processed

                # navigate to the next link
                next_url = response_data["links"]["next"]

                if next_url is not None:
                    logging.debug("Requesting url %s" % next_url)
                    next_response = self.http.get(next_url, headers=self.headers)
                    if not next_response.ok:
                        raise FailToGetException(next_url, response.status_code)
                    response_data = next_response.json()

        if total_results_processed == 0:
            logging.warning(
                "Could not retrieve any results for the given parameters!\n"
                "Study Id: {0}\nPipeline version: {1}".format(
                    project_id, self.version if self.version else "Not specified"
                )
            )
        elif num_results != total_results_processed:
            logging.warning(
                "Only processed "
                + str(total_results_processed)
                + "/"
                + str(num_results)
                + " results!"
            )
        logging.info("Process " + str(total_results_processed) + " results.")
        print("\n Download complete!")

    def _process_download_page(self, analysis, download_response):
        """Process all the pages from the downloads section.
        This will follow the next link.
        """
        analysis_job_id = analysis["id"]
        analysis_attr = analysis["attributes"]
        experiment_type = analysis_attr["experiment-type"]
        pipeline_version = analysis_attr["pipeline-version"]

        if not download_response.ok:
            logger.error(
                "Error getting the accession download files. Accession %s"
                % analysis_job_id
            )
            logger.error("Skipping...")
        else:
            response_json = download_response.json()
            downloads = response_json.get("data", [])
            for download in downloads:
                download_attr = download["attributes"]
                alias = download_attr["alias"]
                group_type = download_attr["group-type"]
                desc_label = download_attr["description"]["label"]
                download_url = download["links"]["self"]
                self.download_file(
                    download_group_type_key=group_type,
                    description_label=desc_label,
                    experiment_type=experiment_type,
                    result_group=self.result_group,
                    pipeline_version=pipeline_version,
                    file_name=alias,
                    download_url=download_url,
                    project_id=self.project_id,
                    dest_dir=self.output_path,
                )
            # store the metadata for the analysis
            self.store_metadata(analysis, response_json)

            next_page_url = response_json.get("links", {}).get("next")
            if next_page_url:
                next_page_respose = self.http.get(
                    next_page_url,
                    headers=self.headers,
                )
                self._process_download_page(analysis, next_page_respose)

    def process_page(self, response_data, progress_bar):
        """Process an analysis returned page"""
        analyses = response_data.get("data", [])
        processed_counter = 0
        for analysis in tqdm(analyses):

            analysis_job_id = analysis["id"]

            download_response = self.http.get(
                MG_ANALYSES_DOWNLOADS_URL.format(**{"accession": analysis_job_id}),
                headers=self.headers,
            )

            self._process_download_page(analysis, download_response)

            processed_counter += 1
            progress_bar.update(1)

        return processed_counter

    def store_metadata(self, analysis, response_json):
        """
        Store the API response json in a tsv file called <analysis>_metadata.tsv
        This file can be used to make it easier to interpret the downloaded files.
        """
        metadata_file_name = "{}_metadata.tsv".format(self.project_id)
        output_file = os.path.join(
            self.output_path, self.project_id, metadata_file_name
        )
        mode = "a" if os.path.exists(output_file) else "w"
        experyment_type = analysis.get("attributes").get("experiment-type")

        col_names = [
            "analysis_id",
            "name",
            "group_type",
            "description",
            "download_url",
            "pipeline_version",
            "experiment_type",
            # TODO: enable when released for the pipeline
            # "checksum",
            # "checksum_algorithm",
        ]

        with open(output_file, mode) as metada_fd:
            writer = csv.writer(metada_fd, delimiter="\t")
            if mode == "w":
                writer.writerow(col_names)

            for entry in response_json.get("data", []):
                download_attr = entry.get("attributes")
                alias = download_attr.get("alias")
                group_type = download_attr.get("group-type")
                desc_label = download_attr.get("description").get("label")

                download_url = entry.get("links").get("self")

                pipeline_version = (
                    entry.get("relationships").get("pipeline").get("data").get("id")
                )

                # TODO: enable when released for the pipeline
                # checksum = download_attr.get("file-checksum").get("checksum")
                # checksum_algorithm = download_attr.get("file-checksum").get(
                #     "checksum-algorithm"
                # )

                writer.writerow(
                    [
                        analysis["id"],
                        alias,
                        group_type,
                        desc_label,
                        download_url,
                        pipeline_version,
                        experyment_type,
                        # checksum,
                        # checksum_algorithm,
                    ]
                )
