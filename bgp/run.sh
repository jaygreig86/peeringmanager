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

${SCRIPTPATH}/fetch_updates.sh -r ${ROUTER}
${SCRIPTPATH}/push_updates_to_router.sh -r ${ROUTER}
