#!/bin/bash

aws cloudformation describe-stacks --stack-name SQSFIFOQueue --output text --query 'Stacks[*].Outputs[*]'
