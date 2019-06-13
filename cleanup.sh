#!/bin/bash

aws cloudformation delete-stack --stack-name SQSStandardQueue
aws cloudformation delete-stack --stack-name SQSFIFOQueue
aws cloudformation delete-stack --stack-name KinesisStream
