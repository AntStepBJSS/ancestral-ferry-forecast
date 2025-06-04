#!/bin/bash

set -e
pdm export -f requirements --no-hashes> requirements.txt
mkdir -p package
cd package
pip install -r ../requirements.txt --target .
cp ../src/ancestral_ferry_forecast/lambdas/route_processing_lambda.py lambda_function.py
