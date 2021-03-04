
# How to use AWS CodeBuild and Amazon EventBridge rules to schedule jobs in Amazon RDS PostgreSQL

## Introduction
When you want to migrate on-premises database workloads with jobs to AWS, you need to select the right AWS services to schedule the jobs .Database administrators traditionally schedule scripts to run against databases using the system cron on the host where the database is running.  When you migrate such workloads from on premises to a managed database service Amazon Relational Database Service (RDS) , you lose the ability to log into the host instance to schedule cron jobs. 

Newer releases of RDS PostgreSQL starting with version 12.5 enable you to schedule PostgreSQL commands within your database. However, if you have a requirement to orchestrate the RDS jobs and need to integrate with native AWS services such as Amazon Simple Notification Service to send notifications then this post provides an alternate way to schedule  and run RDS jobs using AWS CodeBuild and Amazon EventBridge rules.

## Why use AWS CodeBuild for scheduling jobs?
There are multiple managed services in AWS , such as  AWS Lambda , AWS Batch, Amazon Elastic Container Service (Amazon ECS), AWS Step Functions can be used to run RDS jobs like executing stored procedures , functions or simple SQL statements. As your data grows, jobs might take more than 15mins to run. AWS CodeBuild can natively handle workloads that run for a longer time, in comparison to service like Lambda, which are designed to finish within 15 minutes.

If you want to use AWS batch or Amazon ECS , you need to package your code as a Docker container. AWS CodeBuild is a good option when your job takes more than 15 mins or  you can’t (or don’t want to) package your code as a Docker container or you want to use different programming language runtimes for your jobs. 
 

This post demonstrates how to use the combination of AWS CodeBuild and Amazon EventBridge rules to schedule, and run functions or stored procedures on a RDS PostgreSQL database instance. 

![Alt Text](Architecture-scheduling%20Amazon%20RDS%20jobs%20with%20AWS%20CodeBuild%20and%20Amazon%20EventBridge%20rules.png?raw=true  "Title")

    1. EventBridge triggers a CodeBuild project environment based on your schedule 
    2. CodeBuild retrieves the source code from S3 bucket
    3. CodeBuild retrieves the database credentials from AWS secrets manager
    4. CodeBuild initiates the database connection and executes Postgres stored procedure/function 
    5. CodeBuild events are published to EventBridge
    6. SNS notifies job status to subscribed users



## Prerequisites
Before you begin, you'll need to complete the following prerequisites:

    •	Create or have access to an [AWS account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup).
    
    •	Ensure [git!](https://git-scm.com/downloads) is installed on your machine.
    
    •	Set up and configure [AWS Command Line](http://aws.amazon.com/cli). For instructions, see [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
    
    •	SQL client to connect to RDS database. In this post I used [Dbeaver!](https://dbeaver.io/ ).
    
    •	Email address to receive [SNS](https://aws.amazon.com/sns) notifications.



## Walkthrough
    
    .	Clone the project from the AWS code samples repository
    .	Deploy the CloudFormation template to create the required services
    .	Go to the AWS CloudFormation console and make sure that the resources are created
    . Upload source code to S3 bucket 
    .	Run database scripts and create the required tables and functions
    .	Execute CodeBuild project manually
    .	Verify if batch job is running successfully based on the EventBridge rule



## Clone source code from AWS samples
   Download the files required to set up the environment. Refer to the following commands and files:

    $ git clone https://github.com/aws-samples/aws-codebuild-rds-job-scheduling
    $ cd aws-codebuild-rds-job-scheduling
    CreateFunct.sql - Has a code to create sample SQL function. AWS CodeBuild project is configured to execute this SQL function.
    Jobschedulingcft.yml - Defines all the AWS resources required for this solution.
    invokepostgresqldbpy.zip - Contains buildspec.yml and a python script. CodeBuild installs the libraries such as boto3 , psycopg2 defined in the buildspec.yml and invokes the python script which has a code to connect to PostgreSQL database and execute the SQL function


## Deploy the AWS CloudFormation template
    To deploy the CloudFormation template, complete the following steps:
        	1.	Update email address parameter in the CloudFormation template Jobschedulingcft.yml. The email address will be used by Amazon SNS to send a notification about the job status
        2.	Run the CloudFormation template to provision the required services. See the following command for macOS or Linux:
        $ aws cloudformation create-stack --stack-name codebuildjob --template-body file://Jobschedulingcft.yml --capabilities CAPABILITY_NAMED_IAM --region us-east-1

        Output:

        {
        "StackId": "arn:aws:cloudformation:us-east-1:xxxxxxxx:stack/codebuildjob/aade45d0-0415-11eb-9c12-0ed4f058f52d"
         }
    The template will create the following resources:
    •	AWS CodeBuild project
    •	A PostgreSQL instance
    •	S3 bucket
    •	AWS Secrets Manager with PostgreSQL database login credentials
    •	EventBridge rule to trigger the job every day at 10 AM (UTC)
    •	IAM Service Roles for CodeBuild, EventBridge and SNS 
    •	SNS Topic to send notifications to the provided email address with the status of the executed Job

## Upload source code to S3 bucket
    Go to the AWS CloudFormation console and note down the S3 bucket name in Outputs section of your stack.
    Upload aws-codebuild-rds-job-scheduling/src/invokepostgresqldbpy.zip to S3 bucket using CLI command 
    $ aws s3 cp ./src/invokepostgresqldbpy.zip s3://{your S3 bucket name}



## Code Cleanup
    On the AWS Management Console, navigate to your CloudFormation stack codebuildjob and delete it.
    Alternatively, enter the following code in AWS CLI:
    $ aws cloudformation delete-stack --stack-name codebuildjob

    You can refer [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html#troubleshooting-errors-delete-stack-fails) if the stack deletion fails.


## Security

    See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.


## License

    This library is licensed under the MIT-0 License. See the LICENSE file.
