#!/bin/bash

sf skuid page pull --nomodule --targetusername=csilva@intakedesk.com

modules=Intake_Modules,Old_Pages,Test-DEV,Verification_Modules
for i in $(echo $modules | sed "s/,/ /g")
do
    module=$(echo $i | sed 's/_/ /g')
    echo "sf skuid page pull --module=\"${module}\" --targetusername=csilva@intakedesk.com"
    sf skuid page pull --module="${module}" --targetusername=csilva@intakedesk.com
    sleep 5
done

for i in $(echo $modules | sed "s/,/ /g")
do
    module=$(echo $i | sed 's/_/ /g')
    echo "sf skuid page push --module=\"${module}\" --targetusername=csilva@intakedesk.com"
    sf skuid page push --module="${module}" --targetusername=csilva@intakedesk.com
    sleep 5
done