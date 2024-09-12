#!/bin/bash

# Inputs
LOG_LEVEL=error
TIMEOUT=30
MODULES=''
SF_AUTH_URL=''
TARGET_USERNAME_ALIAS="csilva@intakedesk.com"

echo ""
echo "RUNNING: Install Salesforce CLI"
echo "--------------------------------------------------------------------------------------------------------"
echo "::debug::  SKIPPED: npm install -g @salesforce/cli"
sf version --verbose --json

echo ""
echo "RUNNING: Installing SF Skuid Pages Plugin"
echo "--------------------------------------------------------------------------------------------------------"
echo "::debug::  SKIPPED: echo y | sf plugins install skuid-sfdx"
sf plugins

echo ""
echo "RUNNING: Environment Login"
echo "--------------------------------------------------------------------------------------------------------"
echo "::debug::  SKIPPED: sf org login sfdx-url --set-default --sfdx-url-file <(echo \"$SF_AUTH_URL\")"

echo ""
echo "RUNNING: Checkout source code"
echo "--------------------------------------------------------------------------------------------------------"
echo "::debug::  SKIPPED: 3rd party"


echo ""
echo "RUNNING: SKUID Pages Deployment"
echo "--------------------------------------------------------------------------------------------------------"
echo "::debug:: Using https://github.com/skuid/skuid-sfdx for command reference. Docs outdated."

syncFlags=()
defaultSyncFlags=()

if [ ! -z "${{ inputs.TARGET_USERNAME_ALIAS }}" ]; then
    syncFlags+=( --targetusername=${{ inputs.TARGET_USERNAME_ALIAS }} )
    defaultSyncFlags+=( --targetusername=${{ inputs.TARGET_USERNAME_ALIAS }} )
fi

echo "::debug:: Pages that were changed in this PR"

> diff.txt
git diff --name-only HEAD HEAD^1 -- skuidpages/ >> diff.txt

# local version
diff_file="diff.txt"
deploy=false
pages=""
if [ -f "$diff_file" ]; then
    # Read each line in 'diff.txt' and process it
    while IFS= read -r file; do
        # Check if the file exists
        if [ -f "$file" ]; then
            echo "::debug:: Page being deployed: $file"
            pages+="$file "
            deploy=true
        fi
    done < "$diff_file"
fi

# real version
# deploy=false
# pages=""
# for file in ${{ github.event.pull_request.files.*.filename }}; do
#     if [[ "$file" == *"skuidpages/"* ]]; then
#        echo "::debug:: Page being deployed."
#        pages+="$file "
#        deploy=true
#    fi
# done

echo "::debug::"
echo "::debug:: Deploying pages."
echo "::debug:: Has changes to be deployed? $deploy"
echo "::debug::"

if [ "$deploy" = "true" ]; then
    syncFlags+=( $pages )
    echo "::debug:: Command being executed: sf skuid page push ${syncFlags[@]}"
    # sf skuid page push ${syncFlags[@]}
else
    echo "::debug:: No specific changes to deploy. Attempting full deploy."
    echo "::debug:: Command being executed: sf skuid page push ${syncFlags[@]}"
    # sf skuid page push ${syncFlags[@]}
fi
