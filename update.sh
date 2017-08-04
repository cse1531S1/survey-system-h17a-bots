#!/bin/sh
	
existing_remote=`git remote -v | egrep -o "[git@ | https\:\/\/]*github.com.*git" | uniq`

if [ $# -ne 1 ]; then
	echo "Usage: sh update.sh branch_name"
	echo "Please enter a branch name"
    exit 1
fi
git remote set-url origin git@github.com:cse1531S1/cs1531S2-group-project.git
git pull origin $1
git remote set-url origin $existing_remote
