#!/usr/bin/env bash

set -e

node scripts/render-llm4or.mjs
git add -A
git commit -m 'update'
git push
