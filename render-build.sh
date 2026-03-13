#!/usr/bin/env bash
# exit on error
set -o errexit

# Set Playwright path to a known location
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright

pip install -r requirements.txt
playwright install chromium
