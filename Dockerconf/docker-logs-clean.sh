#!/bin/bash

sudo find /var/lib/docker/containers/ -type f -name '*-json.log' -delete
