#!/bin/bash

aws cloudformation create-stack --stack-name KinesisStream --template-body file://kinesis-data-stream.yaml
