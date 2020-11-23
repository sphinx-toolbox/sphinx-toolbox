#!/bin/bash
# This file is managed by 'repo_helper'. Don't edit it directly.

set -e -x

# Switch to miniconda
source "/home/runner/miniconda/etc/profile.d/conda.sh"
hash -r
conda activate base
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda install anaconda-client
conda info -a

for f in conda/dist/noarch/sphinx-toolbox-*.tar.bz2; do
  [ -e "$f" ] || continue
  echo "$f"
  conda install "$f" || exit 1
  echo "Deploying to Anaconda.org..."
  anaconda -t "$ANACONDA_TOKEN" upload "$f" || exit 1
  echo "Successfully deployed to Anaconda.org."
done

exit 0
