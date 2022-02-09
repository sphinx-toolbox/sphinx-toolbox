#!/usr/bin/env python

# stdlib
import os
import sys

# 3rd party
from github3 import GitHub
from github3.repos import Repository
from packaging.version import InvalidVersion, Version

latest_tag = os.environ["GITHUB_REF_NAME"]

try:
	current_version = Version(latest_tag)
except InvalidVersion:
	sys.exit()

gh: GitHub = GitHub(token=os.environ["GITHUB_TOKEN"])
repo: Repository = gh.repository(*os.environ["GITHUB_REPOSITORY"].split('/', 1))

for milestone in repo.milestones(state="open"):
	try:
		milestone_version = Version(milestone.title)
	except InvalidVersion:
		continue
	if milestone_version == current_version:
		sys.exit(not milestone.update(state="closed"))
