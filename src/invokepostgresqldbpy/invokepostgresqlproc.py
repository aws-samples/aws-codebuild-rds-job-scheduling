import boto3
import base64
from botocore.exceptions import ClientError
import json
import psycopg2
import sys
from os import environ


def job_exec():

    # Get User's input via environment variable.
    secret_name = environ.get('secretname')
    region_name = environ.get('Region')

    global secret
    secret = getSecret(secret_name,region_name) # Connect to RDS DB using a secret stored in secretes manager.

    db_host=secret['host']
    db_user=secret['username']
    db_pwd=secret['password']
    db_name=secret['dbname']
    try:
        conn = psycopg2.connect(database=db_name, user=db_user,password=db_pwd, host=db_host)
        cur = conn.cursor()

        # Call function
        print('Calling  postgresql function concat_lower_or_upper')
        cur.callproc('concat_lower_or_upper', ('hello','world','true'))
        row = cur.fetchone()
        while row is not None:
            print(row)
            row = cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if(conn):
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")

# Retrieves secrets value using boto3 API for secrets manager.
def getSecret(secretName,region_nm):
    # If the secret is not defined, the program execution will be stopped.
    if (secretName is None):
       print("Secret Name can't be null.")
       sys.exit()

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_nm
    )

    try:
        
        get_secret_value_response = client.get_secret_value(
            SecretId=secretName
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
             print ("Error while getting values from secret manager ", e)
    # else:
    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        secret = json.loads(get_secret_value_response['SecretString'])
    return secret

job_exec()
