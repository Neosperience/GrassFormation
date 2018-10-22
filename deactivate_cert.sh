#!/usr/bin/env bash
aws iot update-certificate --certificate-id $1 --new-status INACTIVE
