#!/bin/bash

build_os="${build_os}"
build_type="${build_type}"

exec &> "${userdata_log}"

build_slug="${build_slug}"
export AWS_REGION="${aws_region}"
debug_mode="${debug}"
debug_mode="$${not_a_var}"
