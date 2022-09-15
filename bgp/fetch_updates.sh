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
/usr/bin/env git pull
/usr/bin/env python ${SCRIPTPATH}/build_peers.py ${ROUTER}
/usr/bin/env python ${SCRIPTPATH}/build_customers.py ${ROUTER}
/usr/bin/env python ${SCRIPTPATH}/build_filters.py ${ROUTER}
/usr/bin/env git add -A
/usr/bin/env git commit -m "updated by cronjob"
if [ $? == 0 ]
then
        echo "changes"
fi
/usr/bin/env git push -u origin main
