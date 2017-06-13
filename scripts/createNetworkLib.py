#! /usr/bin/env python

"""
Convert Fugue status output to NetworkStandard records
"""

import sys
import os
import json

IMPORTS = """import Fugue.AWS.EC2 as EC2
import Fugue.AWS as AWS
"""

TYPE = """
export {vpc_name_tag}

{vpc_name_tag}:
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

SUBNET = """EC2.Subnet.external("{subnet_id}", region), # {subnet_name_tag} {az}"""

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

    vpcs = data.get('resources', {}).get('vpcs', {})
    subnets = data.get('resources', {}).get('subnets', {})

    if not subnets:
        print('No subnets detected in fugue status output, exiting')
        sys.exit(0)

    alias = (data.get('alias', None) or data['fid']).lower()

    print(IMPORTS)

    for _, top_level_vpc in vpcs.items():
        tl_vpc_id = top_level_vpc['value']['vpc']['VpcId']
        vpc_name_tag = [t['Value'].lower() for t in top_level_vpc['value']['vpc']['Tags'] if t['Key'] == 'Name'][0]
        comments = []
        public_subnets = []
        private_subnets = []
        for _, top_level_subnet in subnets.items():
            subnet_vpc_id = top_level_subnet['value']['subnet']['VpcId']
            if tl_vpc_id == subnet_vpc_id:
                region = top_level_subnet['region']
                subnet = top_level_subnet['value']['subnet']
                subnet_name_tag = [t['Value'] for t in subnet['Tags'] if t['Key'] == 'Name'][0]
                subnet_id = subnet['SubnetId']
                vpc_id = subnet['VpcId']
                az = subnet['AvailabilityZone']
                is_public = any([v['Value'] == 'public' for v in subnet['Tags']])

                if is_public:
                    public_subnets.append(SUBNET.format(subnet_id=subnet_id,subnet_name_tag=subnet_name_tag,az=az))
                else:
                    private_subnets.append(SUBNET.format(subnet_id=subnet_id,subnet_name_tag=subnet_name_tag,az=az))

        output = TYPE.format(
            alias=alias,
            vpc_name_tag=vpc_name_tag,
            comments='\n'.join(comments),
            region=region,
            vpc_id=vpc_id,
            public_subnets=',\n{}'.format(' ' * INDENT).join(sorted(public_subnets, key = lambda x: x.split()[-1])),
            private_subnets=',\n {}'.format(' ' * INDENT).join(sorted(private_subnets, key = lambda x: x.split()[-1])),
        )

        print(output)

def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
