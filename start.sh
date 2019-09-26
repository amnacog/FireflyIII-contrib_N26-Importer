#!/usr/bin/env bash

cd $(dirname $0)

if [ "$1" == "loop" ]; then
	while :; do
		python3 main.py
		sleep 300
	done
else
	python3 main.py
fi
