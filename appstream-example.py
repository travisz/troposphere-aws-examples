import os

from troposphere import Parameter, Ref, Template, Output
import troposphere.appstream as appstr

from troposphere.ec2 import (
    SecurityGroup,
    SecurityGroupIngress,
    SecurityGroupEgress,
    SecurityGroupRule,
    Tags,
    VPCEndpoint,
)

from troposphere.s3 import Bucket, Private

t = Template()
t.add_version('2010-09-09')

## -- Parameters
VpcName = t.add_parameter(
    Parameter(
        "VpcName",
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

AllowedIP = t.add_parameter(
    Parameter(
        "AllowedIP",
        Description="IP Address (CIDR Format) allowed to reach the AppStream Instance",
        Type="String"
    )
)

AppStreamImageArn = t.add_parameter(
    Parameter(
        "AppStreamImageArn",
        Description="ARN of the image from `aws appstream describe-images`",
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

AppStreamStackName = t.add_parameteR(
    Parameter(
        "AppStreamStackName",
        Description="Name of the AppStream Stack",
        Type="String"
    )
)

AppStreamSettingsGroup = t.add_parameter(
    Parameter(
        "AppStreamSettingsGroup",
        Description="Prefix for the Settings group name",
        Type="String"
    )
)

AppStreamUserFirstName = t.add_parameter(
    Parameter(
        "AppStreamUserFirstName",
        Description="First Name of the New AppStream User",
        Type="String"
    )
)

AppStreamUserLastName = t.add_parameter(
    Parameter(
        "AppStreamUserLastName",
        Description="Last Name of the New AppStream User",
        Type="String"
    )
)

AppStreamUserEmail = t.add_parameter(
    Parameter(
        "AppStreamUserEmail",
        Description="Email Address of the first AppStream User",
        Type="String",
        AllowedPattern="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
        ConstraintDescription="must be a valid email address."
    )
)

FleetTypeParam = t.add_parameter(
    Parameter(
        "FleetTypeParam",
        Description="Type of Fleet",
        Type="String",
        AllowedValues=["ON_DEMAND","ALWAYS_ON"]
    )
)

## -- Resources
AppStreamSG = t.add_resource(
    SecurityGroup(
        "AppStreamSG",
        GroupDescription="Security Group to allow inbound traffic to the AppStream Service",
        VpcId=Ref("VpcName"),
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
        Description="Allow HTTPS to the World",
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

AppStreamFleet = t.add_resource(
    appstr.Fleet(
        "AppStreamFleet",
        ComputeCapacity=appstr.ComputeCapacity(
            DesiredInstances="1",
        ),
        Description="AppStreamFleet",
        DisconnectTimeoutInSeconds="900",
        DisplayName="AppStreamFleet",
        EnableDefaultInternetAccess="true",
        FleetType=Ref(FleetTypeParam),
        IdleDisconnectTimeoutInSeconds="300",
        ImageArn=Ref(AppStreamImageArn),
        InstanceType=Ref(InstanceType),
        MaxUserDurationInSeconds="84600",
        Name="AppStreamFleet",
        Tags=Tags(Name="AppStreamFleet"),
        VpcConfig=appstr.VpcConfig(
            SecurityGroupIds=[Ref("AppStreamSG")],
            SubnetIds=[Ref("SubnetId")],
        ),
        DependsOn="AppStreamSG",
    )
)

AppStreamStack = t.add_resource(
    appstr.Stack(
        "AppStreamStack",
        ApplicationSettings=appstr.ApplicationSettings(
            Enabled="true",
            SettingsGroup=Ref(AppStreamSettingsGroup)
        ),
        Description="App Stream Stack",
        DisplayName="AppStream Stack",
        Name=Ref(AppStreamStackName),
        StorageConnectors=[appstr.StorageConnector(
            ConnectorType="HOMEFOLDERS",
            ResourceIdentifier=Ref(AppStreamSettingsGroup),
        )],
        Tags=Tags(Name="App Stream Stack"),
        DependsOn=["AppStreamFleet"],
    )
)

AppStreamAssociation = t.add_resource(
    appstr.StackFleetAssociation(
        "AppStreamAssociation",
        FleetName=Ref("AppStreamFleet"),
        StackName=Ref("AppStreamStack"),
        DependsOn=[ "AppStreamFleet", "AppStreamStack" ],
    )
)

AppStreamUser = t.add_resource(
    appstr.User(
        "AppStreamUser",
        AuthenticationType="USERPOOL",
        FirstName=Ref(AppStreamUserFirstName),
        LastName=Ref(AppStreamUserLastName),
        UserName=Ref(AppStreamUserEmail),
    )
)

AppStreamUserAssoc = t.add_resource(
    appstr.StackUserAssociation(
        "AppStreamUserAssoc",
        AuthenticationType="USERPOOL",
        SendEmailNotification='true',
        StackName=Ref("AppStreamStack"),
        UserName=Ref(AppStreamUserEmail),
        DependsOn=["AppStreamUser", "AppStreamStack"]
    )
)

## -- Print Template
f1 = open('./' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
