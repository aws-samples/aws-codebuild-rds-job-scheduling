
# Schedule jobs in Amazon RDS for PostgreSQL using AWS CodeBuild and Amazon EventBridge

## Introduction
When you want to migrate on-premises database workloads with jobs to AWS, you need to select the right AWS services to schedule the jobs. Database administrators traditionally schedule scripts to run against databases using the system cron on the host where the database is running. When you migrate such workloads from on premises to a managed database service like Amazon Relational Database Service (Amazon RDS), you lose the ability to log in to the host instance to schedule cron jobs. 

Newer releases of Amazon RDS for PostgreSQL starting with version 12.5 enable you to schedule PostgreSQL commands within your database. However, if you need to orchestrate the Amazon RDS jobs and integrate with native AWS services such as Amazon Simple Notification Service (Amazon SNS) to send notifications, this post provides an alternate way to schedule and run Amazon RDS jobs using AWS CodeBuild and Amazon EventBridge rules.


## Why use AWS CodeBuild for scheduling jobs?
An Amazon RDS job can run stored procedures and functions, extract the data, purge the data, or do any other SQL operations. You can run these jobs with different AWS services, such as AWS Lambda, AWS Batch, Amazon Elastic Container Service (Amazon ECS), and AWS Step Functions. As your data grows, jobs might take more than 15 minutes to run. CodeBuild can natively handle workloads that run for a longer time, in comparison to services like Lambda, which are designed to finish within 15 minutes.

If you want to use AWS Batch or Amazon ECS, you need to package your code as a Docker container. CodeBuild is a good option when your job takes more than 15 minutes or you can’t (or don’t want to) package your code as a Docker container, or you want to use different programming language runtimes for your jobs.

This post demonstrates how to use the combination of CodeBuild and EventBridge rules to schedule and run functions or stored procedures on an RDS for PostgreSQL database instance. 


![Alt Text](Architecture-scheduling%20Amazon%20RDS%20jobs%20with%20AWS%20CodeBuild%20and%20Amazon%20EventBridge%20rules.png?raw=true  "Title")

    1. EventBridge triggers a CodeBuild project environment based on your schedule 
    2. CodeBuild retrieves the source code from an Amazon Simple Storage Service (Amazon S3) bucket.
    3. CodeBuild retrieves the database credentials from AWS secrets manager
    4. CodeBuild initiates the database connection and runs the PostgreSQL stored procedure or function 
    5. CodeBuild events are published to EventBridge
    6. Amazon SNS notifies subscribed users of the job status



## Prerequisites
Before you begin, you need to complete the following prerequisites:
    
   * Create or have access to an [AWS account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup).
   * Ensure [git](https://git-scm.com/downloads) is installed on your machine.
   * Set up and configure the [AWS Command Line](http://aws.amazon.com/cli). For instructions, see [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
   * Have a SQL client to connect to RDS database. In this post I used [Dbeaver](https://dbeaver.io/ ). 
   * Have an email address to receive Amazon[SNS](https://aws.amazon.com/sns) notifications.



## Walkthrough
  The following steps provide a high-level overview of the walkthrough:  

  * Clone the project from the AWS code samples repository.
  * Deploy the AWS CloudFormation template to create the required services.
  * Upload source code to the S3 bucket. 
  * Run database scripts and create the SQL function.
  * Execute CodeBuild project manually.
  * Verify if batch job is running successfully based on the EventBridge rule.



## Clone the source code
Download the files required to set up the environment. See the following code:

   > $ git clone https://github.com/aws-samples/aws-codebuild-rds-job-scheduling

   > $ cd aws-codebuild-rds-job-scheduling
You use the following files:
**CreateFunct.sql** - Has a code to create a sample SQL function. The CodeBuild project is configured to run this SQL function.

**Jobschedulingcft.yml** - Defines all the AWS resources required for this solution.

**invokepostgresqldbpy.zip** - Contains buildspec.yml and a Python script. CodeBuild installs the libraries such as boto3 and psycopg2 defined in the buildspec.yml and invokes the Python script, which has a code to connect to PostgreSQL database and run the SQL function.


## Deploying the CloudFormation template

To deploy the CloudFormation template, complete the following steps:

   * Update the email address parameter in the CloudFormation template Jobschedulingcft.yml. Amazon SNS uses this email address to send a notification about the job status.

   * Run the CloudFormation template to provision the required services. See the following code for macOS or Linux:
        > $ aws cloudformation create-stack --stack-name codebuildjob --template-body file://Jobschedulingcft.yml --capabilities CAPABILITY_NAMED_IAM --region us-east-1

        You receive the following output:
        > {
        "StackId": "arn:aws:cloudformation:us-east-1:xxxxxxxx:stack/codebuildjob/aade45d0-0415-11eb-9c12-0ed4f058f52d"
         }

The template creates the following resources:

   * A CodeBuild project
   * A PostgreSQL instance
   * An S3 bucket
   * Secrets Manager with PostgreSQL database login credentials
   * An EventBridge rule to trigger the job every day at 10:00 AM (UTC)
   * AWS Identity and Access Management (IAM) service roles for CodeBuild, EventBridge, and Amazon SNS
   * An SNS topic to send notifications to the provided email address with the status of the job

## Upload the source code to the S3 bucket
On the AWS CloudFormation console, choose the Outputs tab. Make a note of the S3 bucket name.
Upload aws-codebuild-rds-job-scheduling/src/invokepostgresqldbpy.zip to S3 bucket using CLI command:
 > $ aws s3 cp ./src/invokepostgresqldbpy.zip s3://{*your S3 bucket name*}



## Clean up

To avoid incurring future changes, clean up the resources you created.
   * Delete the S3 objects: 
     > $ aws s3 rm s3://{*your s3 bucket name*} --recursive
   * Delete the CloudFormation stack: 
     > $ aws cloudformation delete-stack --stack-name codebuildjob

Alternatively, [delete the stack on the AWS CloudFormation console](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html). To troubleshoot if stack deletion fails, see [Delete stack fails](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html#troubleshooting-errors-delete-stack-fails).



## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.


## License

This library is licensed under the MIT-0 License. See the LICENSE file.
