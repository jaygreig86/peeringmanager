#!/bin/bash
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -r|--router)
    ROUTER="$2"
    shift # past argument
    shift # past value
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters
if [ -z ${ROUTER} ]
then
        echo "Error: Router not specified"
        echo "-r router.domain.tld"
        exit
fi
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

cd ${SCRIPTPATH}/${ROUTER}

# If folder doesn't exist, we need to create it
if [ $? != 0 ]
then
        mkdir ${SCRIPTPATH}/${ROUTER}
        cd ${SCRIPTPATH}/${ROUTER}
        if [ $? != 0 ]
        then
                echo "Fatal error, cannot change path to ${SCRIPTPATH}/${ROUTER}"
                exit
        fi
fi

# Check if a git repo exists
/usr/bin/env git rev-parse --is-inside-work-tree
if [ $? != 0 ]
then
        echo "First run, create repo"
        /usr/bin/env git init -b main
        /usr/bin/env touch last_run
        /usr/bin/env git add last_run
        /usr/bin/env git commit -m "init repo"
        /usr/bin/env git rev-parse --short HEAD > last_run
        /usr/bin/env git add last_run
        /usr/bin/env git commit -m "first hash"
fi
/usr/bin/env git pull
cd ${SCRIPTPATH}
/usr/bin/env python ${SCRIPTPATH}/build_all.py ${ROUTER}
cd ${SCRIPTPATH}/${ROUTER}
/usr/bin/env git add -A
/usr/bin/env git commit -m "updated by cronjob"
if [ $? == 0 ]
then
        echo "changes"
fi
/usr/bin/env git push -u origin main
