#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 EMBL - European Bioinformatics Institute
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
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlretrieve
import requests

from .utils import (
    API_BASE,
    MG_ANALYSES_URL,
    MG_ANALYSES_DOWNLOADS_URL,
    MG_ANALYSES_URL_INCL_VERSION
)

logger = logging.getLogger(__name__)


def bulk_download(args):
    """
    :param args: List of program arguments.
    """
    logging.info("Running bulk download now...")
    project_id = args.accession
    output_path = args.output_path
    version = args.pipeline
    result_group = args.result_group
    program = BulkDownloader(project_id, output_path, version, result_group)
    program.run()
    logging.info("Program finished.")


class BulkDownloader(object):
    """
        Helper tool allowing to download result data for the specified project
        accession.
    """

    # Maps group types and output folder names
    download_group_types_dict = \
        {'Sequence data': 'sequence_data',
         'Functional analysis': 'functional_annotations',
         'Taxonomic analysis': 'taxonomic_annotations',
         'Taxonomic analysis SSU rRNA': 'taxonomic_annot_ssu',
         'Taxonomic analysis LSU rRNA': 'taxonomic_annot_lsu',
         'Statistics': 'stats',
         'non-coding RNAs': 'non_coding_rna'}

    # Set of files, which should be ignored for amplicon datasets
    non_amplicon_file_labels = {'Predicted CDS with annotation',
                                'Predicted CDS without annotation',
                                'Processed reads with annotation',
                                'Processed reads without annotation',
                                'Predicted ORF without annotation',
                                'Processed reads with pCDS'}

    pipeline_version_mapper = {'4.1': '5',
                               '4.0': '4',
                               '3.0': '3',
                               '2.0': '2',
                               '1.0': '1'}

    def __init__(self, project_id, output_path, version, result_group):
        self.project_id = project_id
        self.output_path = output_path
        self.version = version
        self.result_group = result_group
        self._init_program()

    @staticmethod
    def check_config_value(config, key):
        if not config[key]:
            logging.error(
                "Missing ** %s ** setting in the default config "
                "file!" % key)

            sys.exit(1)

    @staticmethod
    def create_subdir_folder(dest_dir, project_id, version,
                             subdir_folder_name):
        sub_dir = Path(
            os.path.join(dest_dir, project_id, version, subdir_folder_name))
        logging.debug("Creating new path: " + str(sub_dir))
        from distutils.version import LooseVersion
        if LooseVersion(platform.python_version()) < LooseVersion("3.6"):
            if not sub_dir.is_dir():
                sub_dir.mkdir(parents=True)
        else:
            sub_dir.mkdir(parents=True, exist_ok=True)
        return sub_dir

    @staticmethod
    def download_resource_by_url(url, output_file_name):
        """
        Kicks off a download and stores the file at the given path.

        :param url: Resource location.
        :param output_file_name: Path of the output file.
        :return:
        """
        logging.debug("Starting the download of the following file...")
        logging.debug(url)
        logging.debug("Saving file in:\n" + output_file_name)

        try:
            urlretrieve(url, output_file_name)
        except URLError as url_error:
            logging.error(url_error)
            raise
        except IOError as io_error:
            logging.error(io_error)
            raise
        logging.debug("Download finished.")

    def download_file(self, download_group_type_key, description_label,
                      experiment_type, pipeline_version,
                      result_group, file_name, download_url, dest_dir,
                      project_id):
        download_group_type_value = \
            self.download_group_types_dict.get(
                download_group_type_key)
        # TODO: Remove the following if case if EMG-742 is resolved
        if experiment_type == 'amplicon' and description_label \
                in self.non_amplicon_file_labels:
            return
            # TODO: Remove the following if case if EMG-741 is resolved
        elif description_label == 'Phylogenetic tree' \
                and pipeline_version == '2.0':
            return
        if result_group \
                and result_group != download_group_type_value:
            return
        else:
            subdir_folder_name = \
                self.download_group_types_dict.get(
                    download_group_type_key)
            sub_dir = BulkDownloader. \
                create_subdir_folder(dest_dir,
                                     project_id,
                                     pipeline_version,
                                     subdir_folder_name)
            output_file_name = os.path.join(dest_dir, str(sub_dir),
                                            file_name)
            BulkDownloader.download_resource_by_url(
                download_url, output_file_name)

    def _get_pipeline_version(self, version):
        return self.pipeline_version_mapper.get(version)

    def _init_program(self):

        if not self.output_path:
            self.output_path = os.getcwd()

        # Print out the program settings
        self._print_program_settings()

    def _print_program_settings(self):
        logging.info("Running the program with the following setting...")
        logging.info("Project: %s" % self.project_id)

        logging.info("Pipeline version: %s"
                     % self.version if self.version else 'Pipeline version: '
                                                         'Not specified')
        logging.info("Result group: %s" %
                     self.result_group if self.result_group else
                     'Result group: Not specified')
        logging.info("API_BASE: %s" % API_BASE)
        logging.info("Output directory: %s" % self.output_path)
        logging.debug("Python version: " + platform.python_version())

    def run(self):
        project_id = self.project_id
        version = self._get_pipeline_version(self.version)
        dest_dir = self.output_path
        result_group = self.result_group

        headers = {
            'Accept': 'application/vnd.api+json',
        }
        params = {
            'accession': project_id,
            'page_size': 5,
        }
        if version:
            params['pipeline_version'] = version
            response = requests.get(
                MG_ANALYSES_URL_INCL_VERSION.format(**params),
                headers=headers)
        else:
            response = requests.get(
                MG_ANALYSES_URL.format(**params),
                headers=headers)

        analyses = response.json()['data']
        counter = 0
        for analysis in analyses:
            analysis_job_id = analysis.get('id')
            analysis_attr = analysis['attributes']
            experiment_type = analysis_attr['experiment-type']
            pipeline_version = analysis_attr['pipeline-version']

            download_response = requests.get(
                MG_ANALYSES_DOWNLOADS_URL.format(
                    **{'accession': analysis_job_id}),
                headers=headers)
            downloads = download_response.json()['data']
            for download in downloads:
                download_attr = download['attributes']
                alias = download_attr['alias']
                group_type = download_attr['group-type']
                desc_label = download_attr['description']['label']
                download_url = download['links']['self']
                counter += 1
                self.download_file(
                    download_group_type_key=group_type,
                    description_label=desc_label,
                    experiment_type=experiment_type,
                    result_group=result_group,
                    pipeline_version=pipeline_version,
                    file_name=alias,
                    download_url=download_url,
                    project_id=project_id,
                    dest_dir=dest_dir
                )

        if counter == 0:
            logging.warning(
                "Could not retrieve any results for the given parameters!\n"
                "Study Id: {0}\nPipeline version: {1}".format(
                    project_id,
                    self.version if self.version else 'Not specified'))
