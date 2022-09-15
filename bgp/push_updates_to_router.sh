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
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )/${ROUTER}"
cd ${SCRIPTPATH}
git clean -f
git reset --hard
git pull

prefix="config/"

as_path_update=$(/usr/bin/env git diff --name-only `cat ${SCRIPTPATH}/last_run` HEAD | egrep "\.aspaths")
echo "Pushing ASPath Changes"
echo "" > aspath.changes
for i in $as_path_update;
do
        if [ -f "$i" ]; then
                if [[ $(wc -l <$i) -ge 1 ]]
                then
                        echo "Updating " $i;
                        scp $i rancid@${ROUTER}:/mnt/flash/bgp/;
                        x=${i#$prefix};
                        x=${x/.aspaths/};
                        if [[ $(wc -l <$i) -ge 100 ]] # When we refresh we need to leave a long enough gap for larger lists
                        then
                                echo "refresh ip as-path access-list $x; bash sleep 30" >> aspath.changes;
                        else
                                echo "refresh ip as-path access-list $x; bash sleep 10" >> aspath.changes;
                        fi
                        changes=1
                fi
        fi
done
if [[ "${#as_path_update}" -gt "1" ]]
then
        /usr/local/rancid/bin/clogin -x aspath.changes ${ROUTER}
fi

echo "ASPath complete. Waiting 10 seconds"
sleep 10


v4_prefix_update=$(/usr/bin/env git diff --name-only `cat ${SCRIPTPATH}/last_run` HEAD | egrep "\.ipv4")
echo "Pushing IPv4 Changes"
echo "" > ipv4.changes
for i in $v4_prefix_update;
do
        if [ -f "$i" ]; then
                if [[ $(wc -l <$i) -ge 1 ]]
                then
                        echo "Updating " $i;
                        scp $i rancid@${ROUTER}:/mnt/flash/bgp/;
                        x=${i#$prefix};
                        x=${x/./-};
                        if [[ $(wc -l <$i) -ge 100 ]] # When we refresh we need to leave a long enough gap for larger lists
                        then
                                echo "refresh ip prefix-list $x-in; bash sleep 30" >> ipv4.changes;
                        else
                                echo "refresh ip prefix-list $x-in; bash sleep 10" >> ipv4.changes;
                        fi
                        changes=1
                fi
        fi
done
if [[ "${#v4_prefix_update}" -gt "1" ]]
then
        /usr/local/rancid/bin/clogin -x ipv4.changes ${ROUTER}
fi

echo "IPv4 complete. Waiting 10 seconds"
sleep 10

v6_prefix_update=$(/usr/bin/env git diff --name-only `cat ${SCRIPTPATH}/last_run` HEAD | egrep "\.ipv6")
echo "Pushing IPv6 Changes"
echo "" > ipv6.changes
for i in $v6_prefix_update;
do
        if [ -f "$i" ]; then
                if [[ $(wc -l <$i) -ge 1 ]]
                then
                        echo "Updating " $i;
                        scp $i rancid@${ROUTER}:/mnt/flash/bgp/;
                        x=${i#$prefix};
                        x=${x/./-};
                        if [[ $(wc -l <$i) -ge 100 ]] # When we refresh we need to leave a long enough gap for larger lists
                        then
                                echo "refresh ipv6 prefix-list $x-in; bash sleep 30" >> ipv6.changes;
                        else
                                echo "refresh ipv6 prefix-list $x-in; bash sleep 10" >> ipv6.changes;
                        fi
                        changes=1
                fi
        fi
done
if [[ "${#v6_prefix_update}" -gt "1" ]]
then
        /usr/local/rancid/bin/clogin -x ipv6.changes ${ROUTER}
fi
echo "IPv6 complete."
cd ${SCRIPTPATH}
git clean -f
git reset --hard

if [[ $changes -gt 0 ]]
then
        git rev-parse --short HEAD > last_run
        git add -A
        git commit -m "pushed to router"
        git push -u origin main
        echo "Changes pushed to the router"
fi
