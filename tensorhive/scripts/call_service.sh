#!/usr/bin/env bash
curl -i -X POST -H 'Content-Type: application/json' -d "{\"jsonrpc\": \"2.0\", \"method\": \"$3\", \"params\": [${@:4}], \"id\": \"1\"}" "http://$1:$2"
