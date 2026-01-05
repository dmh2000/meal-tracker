#!/bin/sh

echo `pgrep -a python | grep meals`
pgrep -a python | grep meals | awk '{print $1}' | xargs kill 2> /dev/null



