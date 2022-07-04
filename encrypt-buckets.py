import argparse

import boto3

default_encryption_rules = {
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256',
                },
            },
        ]
    }

def main():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        try:
            enc_response = response = s3.get_bucket_encryption(Bucket=bucket_name)
            print(f'Bucket: "{bucket_name}", Encryption: {enc_response}')

        except s3.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] != 'ServerSideEncryptionConfigurationNotFoundError':
                raise
            print(f'Bucket: "{bucket_name}", Encryption: None, setting encryption')
            response = s3.put_bucket_encryption(Bucket=bucket_name, 
                                                ServerSideEncryptionConfiguration=default_encryption_rules)
            print(response)
        print('====================================')
if __name__ == '__main__':
    main()
