#!/bin/bash

aws cloudformation create-stack --stack-name SQSFIFOQueue --template-body file://sqs-fifo-queue.yaml
