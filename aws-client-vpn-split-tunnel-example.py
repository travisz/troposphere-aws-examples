import os

# Certificate Manager is a custom Troposphere Plugin. Install it through pip:
# https://pypi.org/project/troposphere-dns-certificate/
import troposphere_dns_certificate.certificatemanager as certmgr

from troposphere import Parameter, Ref, Template, Join, GetAtt, Output
from troposphere.awslambda import Function, Code
from troposphere.cloudformation import AWSCustomObject
from troposphere.directoryservice import (
    VpcSettings,
    SimpleAD,
)
import troposphere_dns_certificate.certificatemanager as certmanager
from troposphere.ec2 import (
    ClientVpnEndpoint,
    ClientVpnRoute,
    ClientVpnTargetNetworkAssociation,
    ClientVpnAuthorizationRule,
    ClientAuthenticationRequest,
    ConnectionLogOptions,
    DirectoryServiceAuthenticationRequest,
    Tags,
    TagSpecifications,
)
from troposphere.iam import Role
from troposphere.ssm import (
    Parameter as SSMParameter,
)

### -- Start the Template
t = Template()
t.set_version('2010-09-09')

### -- Custom Resource
class CustomPassword(AWSCustomObject):
    resource_type = "Custom::Password"

    props = {
        'ServiceToken': (str, True),
        'Length': (int, True)
    }

### -- Parameters
ClientCidr = t.add_parameter(
    Parameter(
        "ClientCidr",
        Description="CIDR Range of the VPN",
        Default="10.0.0.0/22",
        Type="String",
    )
)

VpcName = t.add_parameter(
    Parameter(
        "VpcName",
        Description="ID of the VPC",
        Type="String",
    )
)

TargetCidrRange = t.add_parameter(
    Parameter(
        "TargetCidrRange",
        Description="IP Range within the VPC that you want access to over the VPN",
        Type="String"
        Default="172.18.0.0/16"
    )
)

PublicSubnetIds = t.add_parameter(
    Parameter(
        "PublicSubnetIds",
        Description="Comma Delimited List of Subnet IDs",
        Type="CommaDelimitedList",
    )
)

PublicSubnetParam1A = t.add_parameter(
    Parameter(
        "PublicSubnetParam1A",
        Type="String"
    )
)

PublicSubnetParam2B = t.add_parameter(
    Parameter(
        "PublicSubnetParam2B",
        Type="String"
    )
)

PrivateSubnetIds = t.add_parameter(
    Parameter(
        "PrivateSubnetIds",
        Description="StringList of Private Subnet IDs for the VPC",
        Type="CommaDelimitedList",
    )
)

PrivateSubnetParam1A = t.add_parameter(
    Parameter(
        "PrivateSubnetParam1A",
        Description="Private subnet 1",
        Type="String"
    )
)

PrivateSubnetParam1B = t.add_parameter(
    Parameter(
        "PrivateSubnetParam1B",
        Description="Private subnet 2",
        Type="String"
    )
)

SimpleADSize = t.add_parameter(
    Parameter(
        "SimpleADSize",
        Description="Select the size for the SimpleAD Instance",
        Default="Small",
        AllowedValues=[ 'Small', 'Large' ],
        Type="String"
    )
)

SimpleADDescription = t.add_parameter(
    Parameter(
        "SimpleADDescription",
        Description="Add a Description for the SimpleAD Instance",
        Type="String"
    )
)

SimpleADName = t.add_parameter(
    Parameter(
        "SimpleADName",
        Description="Enter a name for the SimpleAD Instance (ex: corp.example.com)",
        Type="String",
    )
)

DNSHostName = t.add_parameter(
    Parameter(
        "DNSHostName",
        Type="String",
        Description="Hostname of the Certificate to be Created",
    )
)

HostedZone = t.add_parameter(
    Parameter(
        "HostedZone",
        Type="String",
        Description="Id of the Hosted Zone the DNS records need to be created in"
    )
)

## -- Lambda Code
code = [
    "import base64",
    "import json",
    "import logging",
    "import string",
    "import secrets",
    "import random",
    "import boto3",
    "from botocore.vendored import requests",
    "import cfnresponse",
    "",
    "logger = logging.getLogger()",
    "logger.setLevel(logging.INFO)",
    "",
    "def random_string(size=12):",
    "  alphabet = string.ascii_letters + string.digits + string.punctuation",
    "  return ''.join(secrets.choice(alphabet) for _ in range(size))",
    "",
    "def lambda_handler(event, context):",
    "  logger.info('got event {}'.format(event))",
    "  responseData = {}",
    "",
    "  if event['RequestType'] == 'Create':",
    "    number = int(event['ResourceProperties'].get('Length', 12))",
    "    rs = random_string(number)",
    "    responseData['final'] = rs",
    "",
    "  else: # delete / update",
    "    rs = event['PhysicalResourceId']",
    "    responseData['final'] = rs",
    "",
    "  logger.info('responseData {}'.format(responseData))",
    "  cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, responseData['final'])",
]

## -- Resources
LambdaExecutionRole = t.add_resource(
    Role(
        "LambdaExecutionRole",
        AssumeRolePolicyDocument={
            'Statement': [{
                'Effect': 'Allow',
                'Principal': {'Service': ['lambda.amazonaws.com']},
                'Action': ["sts:AssumeRole"]
            }]
        },
    )
)

LambdaFunction = t.add_resource(
    Function(
        "LambdaFunction",
        Code=Code(
            ZipFile=Join("\n", code),
        ),
        Handler="index.lambda_handler",
        Role=GetAtt("LambdaExecutionRole", "Arn"),
        Timeout=30,
        Runtime="python3.6"
    )
)

LambdaPassword = t.add_resource(
    CustomPassword(
        "LambdaPassword",
        Length=22,
        ServiceToken=GetAtt("LambdaFunction", "Arn")
    )
)

ADDomain = t.add_resource(
    SimpleAD(
        "ADDomain",
        Description=Ref(SimpleADDescription),
        Name=Ref(SimpleADName),
        Password=Ref(LambdaPassword),
        Size=Ref(SimpleADSize),
        VpcSettings=VpcSettings(
                SubnetIds=Ref("PublicSubnetIds"),
                VpcId=Ref(VpcName)
        )
    )
)

TestCertificate = t.add_resource(certmgr.Certificate(
    'TestCertificate',
    ValidationMethod='DNS',
    DomainName=Ref(DNSHostName),
    DomainValidationOptions=[
        certmgr.DomainValidationOption(
            DomainName=Ref(DNSHostName),
            HostedZoneId=Ref(HostedZone),
        )
    ],
    Tags=[{
        'Key': 'Name',
        'Value': 'Test Cert'
    }]
))

TestClientVpnEndpoint = t.add_resource(
    ClientVpnEndpoint(
        "TestClientVpnEndpoint",
        AuthenticationOptions=[
            ClientAuthenticationRequest(
                Type="directory-service-authentication",
                ActiveDirectory=DirectoryServiceAuthenticationRequest(
                    DirectoryId=Ref("ADDomain")
                ),
            )
        ],
        ClientCidrBlock=Ref(ClientCidr),
        ConnectionLogOptions=ConnectionLogOptions(
            Enabled=False),
        Description="Test Client VPN Endpoint",
        DnsServers=GetAtt("ADDomain", "DnsIpAddresses"),
        ServerCertificateArn=Ref("TestCertificate"),
        TagSpecifications=[
            TagSpecifications(
                ResourceType="client-vpn-endpoint",
                Tags=Tags(Purpose="Production"),
            )
        ],
        TransportProtocol="udp",
        SplitTunnel=True,
    )
)

AssociateVPNEndpoint1 = t.add_resource(
    ClientVpnTargetNetworkAssociation(
        "AssociateVPNEndpoint1",
        ClientVpnEndpointId=Ref(TestClientVpnEndpoint),
        SubnetId=Ref(PublicSubnetParam1A),
    )
)

AssociateVPNEndpoint2 = t.add_resource(
    ClientVpnTargetNetworkAssociation(
        "AssociateVPNEndpoint2",
        ClientVpnEndpointId=Ref(TestClientVpnEndpoint),
        SubnetId=Ref(PublicSubnetParam2B),
    )
)

ClientVPNAuthRule1 = t.add_resource(
    ClientVpnAuthorizationRule(
        "ClientVPNAuthRule1",
        ClientVpnEndpointId=Ref(TestClientVpnEndpoint),
        AuthorizeAllGroups=True,
        TargetNetworkCidr=Ref(TargetCidrRange),
        Description="Access to Private VPC Network"
    )
)

### -- Output
OutputPassword = t.add_resource(
    SSMParameter(
        "OutputPassword",
        Name="/AD/ADAdminPassword",
        Type="String",
        Value=Ref(LambdaPassword),
        Description="AD Admin Password"
    )
)

OutputVPNEndpoint = t.add_resource(
    SSMParameter(
        "OutputVPNEndpoint",
        Name="/VPN/OutputVPNEndpoint",
        Type="String",
        Value=Ref(TestClientVpnEndpoint),
        Description="Id of the AWS Client VPN"
    )
)

## -- Print Template
f1 = open('../' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
