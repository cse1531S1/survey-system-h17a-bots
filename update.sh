#!/bin/sh

existing_remote = git remote -v | egrep -o "[git | https]*github.com.*git" | uniq

git remote set-url origin git@github.com:cse1531S1/assignment-1-starter.git
git pull origin $1
git remote set-url origin $existing_remote
