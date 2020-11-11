#!/bin/bash
# This file is managed by 'repo_helper'. Don't edit it directly.

set -e -x

if [ "$TRAVIS_PYTHON_VERSION" == 3.6 ]; then
  if [ -z "$TRAVIS_TAG" ] && [ "$TRAVIS_COMMIT_MESSAGE" == "Bump version*" ]; then
    echo "Deferring building conda package because this is release"
  else

    python3 -m pip install repo_helper || exit 1
    python3 -m repo_helper make-recipe || exit 1

    # Switch to miniconda
    source "/home/travis/miniconda/etc/profile.d/conda.sh"
    hash -r
    conda activate base
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    conda install conda-build
    conda install anaconda-client
    conda info -a

    conda config --add channels domdfcoding || exit 1

    conda config --add channels conda-forge || exit 1

    conda build conda -c domdfcoding -c conda-forge --output-folder conda/dist --skip-existing

    for f in conda/dist/noarch/sphinx-toolbox-*.tar.bz2; do
      [ -e "$f" ] || continue
      echo "$f"
      conda install "$f" || exit 1
      echo "Deploying to Anaconda.org..."
      anaconda -t "$ANACONDA_TOKEN" upload "$f" || exit 1
      echo "Successfully deployed to Anaconda.org."
    done

  fi

else
  echo "Skipping deploying conda package because this is not the required runtime"
fi

exit 0
