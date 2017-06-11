#! /usr/bin/env python

"""
Usage: Gen.py FUGUE_STATUS_OUTPUT

Convert Fugue status output to NetworkStandard records

"""

import sys
import json

TYPE = """import Fugue.AWS.EC2 as EC2
import Fugue.AWS as AWS

{comments}
{alias}:
  let region: Optional.unpackOrError(
    AWS.Region.fromString("{region}"),
    "Failed looking up the region by name")
  {{
    region: region,
    vpc: EC2.Vpc.external("{vpc_id}", region),
    subnets: {{
      publicSubnets: [
        {public_subnets}
      ],
      privateSubnets: [
        {private_subnets}
      ],
    }}
  }}
"""

SUBNET = """EC2.Subnet.external("{subnet_id}", region)"""
COMMENT = """# vpc: {vpc_id}, subnet: {subnet_id}, availability zone: {availability_zone}"""

INDENT = 8

private_subnets = []
public_subnets = []
comments = []


def main(args):
    try:
        if sys.stdin.isatty() and len(args) == 2:
            f = open(sys.argv[1], "r")
        elif not sys.stdin.isatty():
            f = sys.stdin
        else:
            usage()
    except FileNotFoundError:
        sys.exit('File not found')

    data = json.load(f)
    f.close()

    subnets = data.get('resources', {}).get('subnets', {})

    if not subnets:
        print('No subnets detected in fugue status output, exiting')
        sys.exit(0)

    alias = (data.get('alias', None) or data['fid']).lower()

    for _, top_level_subnet in subnets.items():
        for _, top_level_subnet in
        region = top_level_subnet['region']
        subnet = top_level_subnet['value']['subnet']
        subnet_id = subnet['SubnetId']
        vpc_id = subnet['VpcId']
        availability_zone = subnet['AvailabilityZone']
        is_public = any([v['Value'] == 'public' for v in subnet['Tags']])

        comments.append(COMMENT.format(
            vpc_id=vpc_id,
            subnet_id=subnet_id,
            availability_zone=availability_zone,
        ))

        if is_public:
            public_subnets.append(SUBNET.format(subnet_id=subnet_id))
        else:
            private_subnets.append(SUBNET.format(subnet_id=subnet_id))

        output = TYPE.format(
            alias=alias,
            comments='\n'.join(comments),
            region=region,
            vpc_id=vpc_id,
            public_subnets=',\n{}'.format(' ' * INDENT).join(public_subnets),
            private_subnets=',\n {}'.format(' ' * INDENT).join(private_subnets),
        )

        print(output)


def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
