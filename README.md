
# How to use AWS CodeBuild and Amazon CloudWatch rules to schedule jobs in Amazon RDS PostgreSQL

## Introduction
When you want to migrate on-premises database workloads with jobs to AWS, you need to select right AWS services to schedule the jobs as you traditionally schedule scripts to run against databases using the system cron on the host where the database is running. As a managed database service, Amazon Relational Database Service (RDS) does not provide access to the underlying infrastructure, so if you migrate such workloads from on premises, you must move these jobs. The latest feature in RDS PostgreSQL versions 12.5 and higher enables you to schedule PostgreSQL commands within your database. However, if you have older RDS PostgreSQL version and need a flexibility to handle multiple batch jobs with an option to customize the notification then this post provides an alternate way to schedule and run jobs using AWS CodeBuild and Amazon CloudWatch rules.

AWS CodeBuild is a managed service that managed continuous integration service that compiles source code, runs tests, and produces software packages that are ready to deploy. With CodeBuild, you don’t need to provision, manage, and scale your own build servers. CodeBuild scales continuously and processes multiple builds concurrently, so your builds are not left waiting in a queue.

Why AWS CodeBuild?
There are different managed services  like Lambda , AWS batch, ECS , Stepfunctions in AWS that can be used to run jobs. As your data grows, jobs might take more than 15mins to run , hence Lambda may not fit as it has execution time limit of 15mins. You need to package your code as a Docker container if you want to use AWS batch or ECS. AWS CodeBuild is a good option if your job is taking more than 15 mins and you can’t (or don’t want to) package your code as a Docker container.
This post demonstrates how to use the combination of AWS CodeBuild and Amazon CloudWatch rules to dynamically provision resources and schedule and run functions or stored procedures on PostgreSQL database. 

Please follow the blog post to schedule jobs and test in you account.

![Alt text]
(Architecture-scheduling Amazon RDS jobs with AWS CodeBuild and Amazon CloudWatch rules.png?raw=true "Title")


## Prerequisites
    Before you get started, complete the following prerequisites:

    •	AWS account.
    •	Install git on your machine.
    •	Set up and configure AWS CLI. For instructions, see Installing the AWS CLI.
    •	SQL client to connect to RDS database. In this post I used Dbeaver
    •	S3 bucket to store the source code
    •	Email address to receive SNS notifications.


## Walkthrough
    The following steps provide a high-level overview of the walkthrough:


    1.	Clone the project from the AWS code samples repository
    2.	Upload source code to S3 bucket and update S3 bucket parameter name in CloudFormation template
    3.	Deploy the CloudFormation template to create the required services
    4.	Go to the AWS CloudFormation console and make sure that the resources are created
    5.	Run database scripts and create the required tables and functions
    6.	Execute CodeBuild project manually
    7.	Verify if batch job is running successfully based on the CloudWatch rule



## Clone source code from AWS samples
    Download the files required to set up the environment. See the following code:

    $ git clone https://github.com/aws-samples/aws-codebuild-rds-job-scheduling (Creating this repo is in progress)
    $ cd aws-codebuild-rds-job-scheduling
    CreateSampleDataAndFunct.sql has a code to create sample tables and functions.
    Jobschedulingcft.yaml defines all the AWS resources required for this solution.
    Invokepostgresqldbpy.zip contains buildspec.yml and a python script.

## Upload source code to S3 bucket
    Upload aws-codebuild-rds-job-scheduling/src/invokepostgresqldbpy.zip to S3 bucket. This package contains buildspec.yml and a python script invokepostgresqlproc.py. CodeBuild installs the libraries defined in the buildspec.xml and invokes invokepostgresqlproc.py which has a code to connect to postgresql database and execute the function.


## Deploy the AWS CloudFormation template
    To deploy the CloudFormation template, complete the following steps:
    1.	Update the S3bucket name where source code is uploaded and email address parameters in the Jobschedulingcft.yaml
    2.	Run the CloudFormation template to provision the required services. See the following code:
    $ aws cloudformation create-stack --stack-name codebuildjob --template-body file://Jobschedulingcft.yaml --capabilities CAPABILITY_NAMED_IAM --region us-east-1
    {
        "StackId": "arn:aws:cloudformation:us-east-1:xxxxxxxx:stack/codebuildjob/aade45d0-0415-11eb-9c12-0ed4f058f52d"
    }

    The template creates the following:

    •	CodeBuild project
    •	PostgreSQL instance
    •	AWS Secrets Manager with PostgreSQL database login credentials
    •	CloudWatch rule to run the CodeBuild project based on the schedule
    •	Roles with appropriate permission
    •	SNS Topic to send notifications with the status of Job


## Testing

    Please follow the blog post to schedule and the test you job execution.


## Code Cleanup

On the AWS Management Console, navigate to your CloudFormation stack codebuildjob and delete it.
Alternatively, enter the following code in AWS CLI:
$ aws cloudformation delete-stack --stack-name codebuildjob


## Security

    See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.


## License

    This library is licensed under the MIT-0 License. See the LICENSE file.
