#!/usr/bin/env bash

host=localhost
port=31333

if [ ! -z "$1" ]; then
    host=$1
fi

if [ ! -z "$2" ]; then
    port=$2
fi

bash call_service.sh "$host" "$port" get_infrastructure
