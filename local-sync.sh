#!/bin/bash

flags=()
username_alias='csilva@intakedesk.com'

if [ ! -z "$username_alias" ]; then
syncFlags+=( --targetusername=$username_alias )
fi

sf skuid page pull --nomodule "${syncFlags[@]}"

modules=Intake_Modules,Old_Pages,Test-DEV,Verification_Modules
for i in $(echo $modules | sed "s/,/ /g")
do
    module=$(echo $i | sed 's/_/ /g')
    echo "sf skuid page pull --module=\"${module}\" \"${syncFlags[@]}\""
    sf skuid page pull --module="${module}" "${syncFlags[@]}"
    sleep 5
done

for i in $(echo $modules | sed "s/,/ /g")
do
    module=$(echo $i | sed 's/_/ /g')
    echo "sf skuid page push --module=\"${module}\" \"${syncFlags[@]}\""
    sf skuid page push --module="${module}" "${syncFlags[@]}"
    sleep 5
done