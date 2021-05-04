#!/bin/bash
# This file is managed by 'repo_helper'. Don't edit it directly.

set -e -x

python -m mkrecipe --type wheel || exit 1

# Switch to miniconda
source "/home/runner/miniconda/etc/profile.d/conda.sh"
hash -r
conda activate base
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda install conda-build
conda install anaconda-client
conda info -a

conda config --add channels conda-forge || exit 1
conda config --add channels domdfcoding || exit 1

conda build conda -c conda-forge -c domdfcoding --output-folder conda/dist --skip-existing

exit 0
