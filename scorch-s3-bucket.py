#!/usr/bin/env python
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--bucket", required=True, help="Bucket name")
parser.add_argument("--prefix", required=False, default="")
parser.add_argument("--verbose", required=False, default=False)
args = parser.parse_args()


client = boto3.client('s3')
Bucket = args.bucket
Prefix = args.prefix
IsTruncated = True
MaxKeys = 1000
KeyMarker = None

while IsTruncated == True:
    if not KeyMarker:
        version_list = client.list_object_versions(
            Bucket=Bucket,
            MaxKeys=MaxKeys,
            Prefix=Prefix
        )
    else:
        version_list = client.list_object_versions(
            Bucket=Bucket,
            MaxKeys=MaxKeys,
            KeyMarker=KeyMarker,
            Prefix=Prefix
        )
    try:
        objects = []
        versions = version_list ['Versions']
        for v in versions:
            objects.append({'VersionId':v['VersionId'],'Key':v['Key']})
            response = client.delete_objects(Bucket=Bucket,Delete={'Objects':objects})
            if args.verbose:
                print (response)
    except:
        pass
    try:
        objects = []
        delete_markers = version_list['DeleteMarkers']
        for d in delete_markers:
            objects.append({'VersionId':d['VersionId'],'Key': d['Key']})
        response = client.delete_objects(Bucket=Bucket,Delete={'Objects':objects})
        if args.verbose:
            print (response)
    except:
        pass

    IsTruncated = version_list['IsTruncated']            
    KeyMarker = version_list.get('NextKeyMarker', None)
    