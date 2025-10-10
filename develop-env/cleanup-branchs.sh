#!/bin/bash

git branch -r | awk -F/ '{print $2}' | sort -u | \
  grep -vxFf <(git branch --format='%(refname:short)' | tr -d '* ') | \
  while read -r branch; do
      echo "lösche $branch"
      git branch -D "$branch"
  done

