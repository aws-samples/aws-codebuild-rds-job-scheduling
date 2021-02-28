
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
    Before you get started, complete the following prerequisites:

    •	AWS account.
    •	Install git on your machine.
    •	Set up and configure AWS CLI. For instructions, see Installing the AWS CLI.
    •	SQL client to connect to RDS database. In this post I used Dbeaver
    •	S3 bucket to store the source code
    •	Email address to receive SNS notifications.


## Walkthrough
    
    1.	Clone the project from the AWS code samples repository
    2.	Upload source code to S3 bucket and update S3 bucket parameter name in CloudFormation template
    3.	Deploy the CloudFormation template to create the required services
    4.	Go to the AWS CloudFormation console and make sure that the resources are created
    5.	Run database scripts and create the required tables and functions
    6.	Execute CodeBuild project manually
    7.	Verify if batch job is running successfully based on the CloudWatch rule



## Clone source code from AWS samples
    Download the files required to set up the environment. See the following code:

    $ git clone https://github.com/aws-samples/aws-codebuild-rds-job-scheduling
    $ cd aws-codebuild-rds-job-scheduling
    createFunct.sql - Has a code to create sample SQL function.
    Jobschedulingcft.yml - Defines all the AWS resources required for this solution.
    invokepostgresqldbpy.zip - Contains buildspec.yml and a python script.


## Upload source code to S3 bucket
    Upload aws-codebuild-rds-job-scheduling/src/invokepostgresqldbpy.zip to S3 bucket. This package contains buildspec.yml and a python script. CodeBuild installs the libraries such as boto3 , psycopg2 defined in the buildspec.yml and invokes invokepostgresqlproc.py which has a code to connect to PostgreSQL database and execute the SQL function.


## Deploy the AWS CloudFormation template
    To deploy the CloudFormation template, complete the following steps:
        1.	Update the S3bucket name where source code is uploaded and email address parameters in the CloudFormation template Jobschedulingcft.yml. The email address will be used by Amazon SNS to send a notification about the job status
        2.	Run the CloudFormation template to provision the required services. See the following command for macOS or Linux:
        $ aws cloudformation create-stack --stack-name codebuildjob --template-body file://Jobschedulingcft.yml --capabilities CAPABILITY_NAMED_IAM --region us-east-1

        Output:

        {
        "StackId": "arn:aws:cloudformation:us-east-1:xxxxxxxx:stack/codebuildjob/aade45d0-0415-11eb-9c12-0ed4f058f52d"
         }
    The template will create the following resources:
        •	CodeBuild project
        •	PostgreSQL instance
        •	AWS Secrets Manager with PostgreSQL database login credentials
        •	EventBridge rule to trigger the job every day at 10 AM (UTC)
        •	IAM Roles for CodeBuild, EventBridge and SNS with appropriate permissions
        •	SNS Topic to send notifications with the status of the Job



## Code Cleanup
    On the AWS Management Console, navigate to your CloudFormation stack codebuildjob and delete it.
    Alternatively, enter the following code in AWS CLI:
    $ aws cloudformation delete-stack --stack-name codebuildjob


## Security

    See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.


## License

    This library is licensed under the MIT-0 License. See the LICENSE file.
