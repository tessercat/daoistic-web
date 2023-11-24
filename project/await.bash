#!/bin/bash
# Await local TCP port.
# Exit when the port is listening or after n tests.
loops=0
max_loops=10
ss_output=$(ss -tlnHp src "127.0.0.1:$1")
echo "$ss_output"
while [ -z "$ss_output" ] && [ $loops -lt $max_loops ]; do
    /bin/sleep 1
    loops=$((loops+1))
    ss_output=$(ss -tlnHp src "127.0.0.1:$1")
done
if [ -z "$ss_output" ]; then
    echo "Local TCP port $1 not found"
    exit 1
fi
echo "Found local TCP port $1"
exit 0
