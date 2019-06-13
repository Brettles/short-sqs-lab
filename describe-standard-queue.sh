#!/bin/bash

aws cloudformation describe-stacks --stack-name SQSStandardQueue --output text --query 'Stacks[*].Outputs[*]'
