#!/usr/bin/env bash

host=localhost
port=31333

if [ "$#" -lt 1 ]; then
    echo  "Usage: $0 <node_hostname> [manager_hostname=$host] [manager_port=$port]"
    exit 1
fi

node=$1

if [ ! -z "$2" ]; then
    host=$2
fi

if [ ! -z "$3" ]; then
    port=$3
fi

bash call_service.sh "$host" "$port" add_node "\"$node\""
