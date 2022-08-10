import json
import boto3

DRY_RUN = True
RUN_ON_NV = True

def main():
    ec2 = boto3.client('ec2')
    # Retrieves all regions/endpoints that work with EC2
    response = ec2.describe_regions()
    ec2_regions = [region['RegionName'] for region in response['Regions']]
    print(ec2_regions)

    if RUN_ON_NV:
        clean_rules_from_default_vpc_sg('us-east-1')
    else:
        for region in ec2_regions:
            clean_rules_from_default_vpc_sg(region)

def clean_rules_from_default_vpc_sg(region: str):
    print(f'+++ Reading VPC details for {region}')
    ec2 = boto3.resource('ec2', region_name=region)
    client = boto3.client('ec2', region_name=region)

    filters = [{'Name':'isDefault', 'Values': ['true']}]

    vpcs = list(ec2.vpcs.filter(Filters=filters))

    print(vpcs)

    for vpc in vpcs:
        response = client.describe_vpcs(VpcIds=[vpc.id])
        print(json.dumps(response, indent=4))

        remove_rules_from_default_sg(ec2_client=client, ec2_resource=ec2, vpc_id=response['Vpcs'][0]['VpcId'])

if __name__ == "__main__":
    main()



def remove_rules_from_default_sg(ec2_client, ec2_resource, vpc_id: str):
    filters=[
        {
            'Name': 'vpc-id',
            'Values': [vpc_id]
        }
    ]

    response=ec2_client.describe_security_groups(Filters=filters)
    print('+++ Security grousp:')
    print(response)

    for security_group in response['SecurityGroups']:
        inbound_rules = security_group['IpPermissions']
        outbound_rules = security_group['IpPermissionsEgress']
        sg_id = security_group['GroupId']

        if inbound_rules or outbound_rules:
            print(f'Warning! security group {sg_id} in default vpc: {vpc_id}, has rules!')
            print(f'{inbound_rules=}, {outbound_rules=}')
            # print('Deleting rules: ')
            # sg = ec2_resource.SecurityGroup(sg_id)
            # sg.revoke_ingress(IpPermissions=inbound_rules, DryRun=DRY_RUN)
            # sg.revoke_egress(IpPermissions=outbound_rules, DryRun=DRY_RUN)
            
        else:
            print(f'Security group {sg_id} in default vpc: {vpc_id}, has no rules')
