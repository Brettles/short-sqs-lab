#!/bin/bash

aws cloudformation describe-stacks --stack-name KinesisStream --output text --query 'Stacks[*].Outputs[*]'
