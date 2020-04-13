import os

from troposphere import GetAtt, Output, Parameter, Ref, Template
import troposphere.appstream as appstr

from troposphere.ec2 import (
    SecurityGroup,
    SecurityGroupIngress,
    SecurityGroupEgress,
    SecurityGroupRule,
    Tags,
)

t = Template()
t.add_version('2010-09-09')

## -- Parameters
VpcId = t.add_parameter(
    Parameter(
        "VpcId",
        Description="ID of the VPC where AppStream is being launched.",
        Type="String",
    )
)

SubnetId = t.add_parameter(
    Parameter(
        "SubnetId",
        Description="ID of the Subnet for AppStream",
        Type="String",
    )
)

AppStreamImageArn = t.add_parameter(
    Parameter(
        "AppStreamImageArn",
        Description="ARN of the base image from `aws appstream describe-images`",
        Type="String"
    )
)

AllowedIP = t.add_parameter(
    Parameter(
        "AllowedIP",
        Description="IP Address (CIDR Format) allowed to reach the AppStream Image Builder Console",
        Type="String"
    )
)

InstanceType = t.add_parameter(
    Parameter(
        "InstanceType",
        Description="Instance Type to use for Image Builder. Restricted to smaller instances but remove the 'AllowedValues' line to access any instance type",
        Type="String",
        AllowedValues=["stream.standard.medium","stream.standard.large"]
    )
)

## -- Resources
AppStreamSG = t.add_resource(
    SecurityGroup(
        "AppStreamSG",
        GroupDescription="Security Group to allow inbound traffic to the AppStream Service",
        VpcId=Ref("VpcId"),
        Tags=Tags(Name="AppStreamSG",Project="AppStream"),
    )
)

AppStreamSGIngress01 = t.add_resource(
    SecurityGroupIngress(
        "AppStreamSGIngress01",
        GroupId=Ref("AppStreamSG"),
        CidrIp=Ref(AllowedIP),
        FromPort="443",
        ToPort="443",
        IpProtocol="tcp",
        Description="Allow HTTPS for Access to the Image Builder",
    )
)

AppStreamEgress = t.add_resource(
    SecurityGroupEgress(
        "AppStreamEgress",
        GroupId=Ref("AppStreamSG"),
        IpProtocol="-1",
        FromPort="0",
        ToPort="65535",
        CidrIp="0.0.0.0/0"
    )
)

AppStreamImageBuilder = t.add_resource(
    appstr.ImageBuilder(
        "AppStreamImageBuilder",
        Description="Image Builder",
        EnableDefaultInternetAccess="true",
        ImageArn=Ref(AppStreamImageArn),
        InstanceType=Ref(InstanceType),
        Name="ImageBuilder",
        Tags=Tags(Name="Image Builder"),
        VpcConfig=appstr.VpcConfig(
            SecurityGroupIds=[Ref("AppStreamSG")],
            SubnetIds=[Ref("SubnetId")],
        ),
        DependsOn="AppStreamSG",
    )
)

## -- Outputs
oStreamingURL = t.add_output(
    Output(
        "StreamingURL",
        Description="Streaming URL for Image Builder Session",
        Value=GetAtt("AppStreamImageBuilder", "StreamingUrl")
    )
)

## -- Print Template
f1 = open('./' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
