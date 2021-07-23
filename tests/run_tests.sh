#!/bin/bash

set -e

echo "Unit tests"

python -m unittest discover unit -v

echo "------------------------"

echo "Integration"

echo "Testing original_metadata"

cd integration

set -x
mg-toolkit -d original_metadata -a ERP001178
set +x

md5sum -c original_metadata/ERP001178.csv.md5
rm ERP001178.csv

echo "Testing bulk_download"

set -x
mg-toolkit -d bulk_download -a MGYS00002478
set +x

md5sum -c bulk_download/ERR169332.5_8S_rRNA.RF00002.fa.md5
md5sum -c bulk_download/MGYS00002478_metadata.tsv.md5
rm -r MGYS00002478

echo "Testing sequence_search"

set -x
mg-toolkit -d sequence_search --sequence sequence_search/test.fasta -db full evalue -E 1.1e-240 -domE 0.01 -incE 1.1e-240 -incdomE 0.01
set +x

mv -f *_sequence_search.csv sequence_search.csv
md5sum -c sequence_search/sequence_search.csv.md5
rm *.csv
