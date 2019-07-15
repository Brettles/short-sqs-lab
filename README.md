# Short SQS and Kinesis Lab
This is a short AWS lab covering [SQS](https://aws.amazon.com/sqs/) messaging, [Kinesis](https://aws.amazon.com/kinesis/data-streams/) data streaming from "traditional" compute (i.e. a virtual machine somewhere) and then looking at how to process those SQS and Kinesis messages in [Lambda](https://aws.amazon.com/lambda/).

## Requirements
You will need an AWS account to run this lab. You can run all of the commands from a Python-enabled virtual machine anywhere with appropriate IAM permissions (or roles if running within AWS) but to make things easier to demonstrated, we will show all of this using [Cloud9](https://aws.amazon.com/cloud9/).

## Lab Instructions
### Cloud9
Create a Cloud9 environment in the AWS console in the region of your choice. Use that region for the rest of this lab. Name the region anything you like and accept all of the default including using the smallest instance type (t2.micro). Once it has started you can continue with the rest of the instructions.

If you choose not to use Cloud9 you will need to have a machine that runs Python and you will need to have permissions to use CloudFormation, SQS, Kinesis, Lambda, CloudWatch Logs and IAM. You could use locally installed credentials or use an IAM role attached to an instance in AWS.

### Clone this repo
To give you easier access to the files, inside your Cloud9 environment you can clone this repository:
```
git clone https://github.com/Brettles/short-sqs-lab
cd short-sqs-lab
```

### SQS Standard Queue Creation
First, we'll set up a SQS standard queue (next we'll look at FIFO). You can set this up manually in the console or using the CLI or you can use the CloudFormation template in `sqs-standard-queue.yaml`. This creates a SQS queue with the name "StandardQueue".

At the CLI, you can run CloudFormation using the instructions [in the documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-cli-creating-stack.html). Alternately, you can run `./create-standard-queue.sh` which calls CloudFormation using those same commands. You can then run `./describe-standard-queue.sh` which will show the stack output once CloudFormation has completed creation.

Whether creating the queue manually or in CloudFormation, take a note of the output with the queue URL - you'll need that next.

### Sending SQS Messages
Edit `generate-sqs-data.py`. On line 10 you'll see `<SQS Queue URL>` - put the SQS queue URL here. You'll find it in the console or in the outputs section of the CloudFormation stack.

If you're using Cloud9 you can find the files in the navigation pane to the left of the screen and double-click on a file to edit it. If you're using your own host then use vi (my favourite) or nano to edit the file.

Save the file and run it:
```
./generate-sqs-data.py
```
You'll see it sending messages to the queue with random data in it. While it's doing that:

### Receiving SQS Messages
Edit `get-sqs-data.py` and edit line 7 with the SQS queue URL again. Save the file and then run it in a new terminal window (leave the other script sending messages).
```
./get-sqs-data.py
```
Note that the messages are numbered and may appear out of order. This is normal for SQS Standard queues.

You may also open a third terminal window and run the script again. Now both scripts are receiving messages but note that you will not see the same message number repeated although note that this is not a guarantee - [messages are delivered at least once](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html#standard-queues-at-least-once-delivery). SQS messages are only delivered to a single receiver.

The code also contains something else important - it deletes the message from the queue once it is done processing it. If the receiver does not delete the message it eventually reappears in the queue. This is controlled by the [visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) - if your message receiver stops unexpectedly, the message will be put back in the queue and be processed by another worker. If the worker is going to take longer than the message timeout to process a message it can change the visibility timeout for that message so that it doesn't reappear in the queue prematurely.

You can now stop the sender and receiver(s) by pressing ^C in each window as appropriate.

### SQS FIFO Queue Creation
A FIFO queue is "First-In, First-Out" and messages are delivered once only. Otherwise they operate almost exactly as standard queues do although the creating of the queue and the code to send messages to the queue are both slightly different.

Create the FIFO queue manually or use the `sqs-fifo-queue.yaml` CloudFormation template (which creates a queue called "FIFOQueue.fifo". Note that the name of the queue must end in ".fifo".

If you are creating the queue manually, enabled "Content-Based Deduplication" which is where SQS uses a SHA-256 hash of the message contents to detect duplicate messages. If this is not enabled, your code must manually create a unqique identifier for each message.

You may also run `./create-fifo-queue.sh` which calls CloudFormation on your behalf. You can then run `./describe-fifo-queue.sh` which will show the stack output once CloudFormation has completed creation.

### Sending FIFO SQS Messages
Edit `generate-sqs-fifo-data.py` on line 10 and modify the SQS Queue URL. Save and run the script:
```
./generate-sqs-fifo-data.py
```

Note that the code is slightly different - when a message is sent to a FIFO queue you must specify a group name. In this example it's set to "Group1". The message receiver can optional choose which group to receive messages from. If you do not specify a group then messages are received from all groups.

### Receiving FIFO SQS Messages
Edit `get-sqs-data.py` again and update it with the FIFO queue URL. Note that the receiving code is the same for standard and FIFO queues.

Run the receiver:
```
./get-sqs-data.py
```
Note that the messages are in numerical order as produced. If you run the receiver in another terminal window you'll notice that the messages are still in order although each window is receiving different messages.

When you're done, stop the sender and receiver(s) by pressing ^C in each terminal window.

### Kinesis vs SQS
A common question is "What's the different between SQS and Kinesis". From a messaging standpoint it comes down to single delivery of messages as compared to multiple "consumers".

With Kinesis you have a message "producer" and a message "consumer" - much the same as the scripts above the send messages to a SQS queue and then receive them. However, each Kinesis data stream can have multiple consumers who each see the same messages. There is no concept in Kinesis for "message visiblity" nor "message deletion" - all consumers see all messages. This can be very handy when you have multiple jobs that need to be performed on a single message - rather than have a single monolithic block of code that handles all tasks, you can have smaller pieces of code that each perform discrete operations based on the same message.

The other advantage of Kinesis is that the consumer can elect where to start in the message stream - either from "now" (which means only receiving new messages); from the start of the stream (reprocessing is back to the retention period (up to 7 days); or from a specific time in the stream.

Scalability is an interesting differentiator here. Both SQS and Kinesis have limits on the number of API calls that can be made in any given timeframe for any client. So if you send or poll too often you may get rate-limited or see messages returned from the service telling you that you're exceeding the limits.

After that, SQS has a much simpler scaling model - which is how many messages you can send and receive (to and from multiple clients). That's it! The service automatically scales to meet your demands.

Kinesis is a bit more complex. For each shard in the message stream you can only send a certain amount of data; and only receive a certain (different) amount. If you want to exceed those limits then you need increase the number of shards you have in your stream. That's pretty easy - but it is a manual (in terms of the service - of course it can be automated) process that the service doesn't do for you. So keep an eye on your data rates on a stream and increase (or decrease) the number of shards appropriately.

Whether you use SQS or Kinesis is up to you - but SQS is better suited to asynchronous decoupling of application components whereas Kinesis is more for streaming of data.

References:
[SQS service limits](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-cli-creating-stack.html)
[Kinesis service limits](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-cli-creating-stack.html)

### Kinesis Data Stream Creation
Create the Kinesis stream manually or using the `kinesis-data-stream.yaml` CloudFormation template. This creates a Kinesis Data Stream called "KinesisStream".

You may also run `./create-kinesis-stream.sh` which calls CloudFormation for you. You can then run `./describe-kinesis-stream.sh` which will show the stack output once CloudFormation has completed creation.

### Sending Kinesis Data
You do not need to edit `generate-kinesis-data.py` as it already has the stream name in it on line 11 (unless you created a stream manually with a different name). As with the SQS script above, this creates random messages. Run it to begin sending messages:
```
./generate-kinesis-data.py
```

### Receiving Kinesis Data
Run the Kinesis data retrieval script in another terminal window:
```
./get-kinesis-data.py
```
Note that we do not see messages with early message numbers on them - this is because this consumer operates from "LATEST" which is the current point in the stream (see line 28 in the code).

Open another terminal window and run the retrieval script again. Note that both consumers are seeing the same messages.

When done, stop all the scripts by pressing ^C.

### SQS and Lambda
A common pattern is to use a Lambda function to process messages from a SQS queue. There are several reasons for this - the main two being the ability of Lambda to scale up (and down) quickly on demand; and that you are only charged for Lambda when your code is running - if there are no messages to process there is no cost as the code isn't running to poll the queue.

This is the other architectural different writing SQS code for Lambda - you do not need to poll the queue. The Lambda service does this for you and executes your Lambda function when messages are received. You can see this by looking at the example code in `lambda-sqs-client.py` - it doesn't have any SQS specific code in it, including deleting the messages that are processed from the queue.

Create a new Lambda function with a Python 3.7 runtime and have Lambda create the basic IAM role for this function (this is the default). Copy and paste the code from `lambda-sqs-client.py`. Now save the function.

Next, we need to add a SQS trigger to the Lambda function where the queue to listen on will be in the form `arn:aws:sqs:<region name>:<account number>:<queue name>` - use "StandardQueue" because that's the queue we created earlier. You'll note that when you try to save the function it will throw an error telling you that the function does not have permission to receive messages from SQS. Even though the code doesn't explicitly call SQS (it is the Lambda service that does this) it still needs appropriate permissions. Earlier, all of the other examples were running using your IAM permissions in Cloud9 (or elsewhere) so the SQS permissions were implicit.

Cancel the creation of the trigger then find the section of the Lambda function definition that shows the IAM role assigned to this function. You'll see a link to the IAM role - click on that to be taken to the IAM role definition. Here you'll see an inline policy that grants the Lambda function access to CloudWatch Logs to create a log group and then write to the log group belonging to that Lambda function. Attach an existing policy to the role called "AWSLambdaSQSQueueExecutionRole".

Now go back to the Lambda function and add the SQS queue as a trigger. In a production environment, you would lock down the IAM permissions so that the Lambda function could only read from a single queue.

In Cloud9, edit `generate-sqs-data.py` again and ensure that the queue URL points to "StandardQueue". Then save and run it again.

In the console, go to CLoudwatch Logs and observe the log for your Lambda function. You can also get there by clicking on the "Monitoring" tab in the Lambda console and then clicking "View logs in CloudWatch".

The log entries will show the messages being processed by Lambda. When you're done, press ^C in the Cloud9 terminal to stop the SQS message producer.

### Kinesis and Lambda
As with SQS, another common pattern is to use Lambda to consume messages from a Kinesis Data Stream.

As above, create a new Lambda function using the code as seen in `lambda-kinesis-client.py`. Once again, note that the code doesn't use any of the Kinesis libraries that were used in the previous Kinesis consumer because Lambda is doing a bunch of work for us. However, the message payload does arrive Base64 encoded so we have to decode that.

As with the previous example, add the Kinesis stream as a trigger noting that you will need to modify the role for this function as well by adding the "AWSLambdaKinesisExecutionRole" policy.

Once done, run `generate-kinesis-data.py` again and observe the logs for this function in CloudWatch Logs. When finished, press ^C.

## Cleaning up
If you used CloudFormation to set up the SQS queues and Kinesis data stream, delete the CloudFormation stacks. If you created them manually, delete them directly from the console. If you used the shell scripts to run CloudFormation, just run `./cleanup.sh` to remove the CloudFormation stacks.

Delete the Lambda functions.

Delete the CloudWatch logs that were created by the Lambda functions

Delete the IAM roles created by the Lambda console for SQS and Kinesis access.

Delete the Cloud9 instance (if you created one).

## Summary
What you have seen here are some simple examples of how to use SQS and Kinesis to distribute messages between application components; some options on how to run the code (standalone or in Lambda); and the IAM permissions required.
