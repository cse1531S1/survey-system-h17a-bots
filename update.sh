#!/bin/sh
	
existing_remote=`git remote -v | egrep -o "[git@ | https\:\/\/]*github.com.*git" | uniq`
echo $existing_remote
echo $#

if [ $# -ne 1 ]; then
	echo "Usage: sh update.sh branch_name"
	echo "Please enter a branch name"
    exit 1
fi
echo git remote set-url origin git@github.com:cse1531S1/assignment-1-starter.git
echo git pull origin $1
echo git remote set-url origin $existing_remote
