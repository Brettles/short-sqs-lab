#!/bin/bash

aws cloudformation create-stack --stack-name SQSStandardQueue --template-body file://sqs-standard-queue.yaml
