import os

from troposphere import Parameter, Ref, Template, Join, AWS_ACCOUNT_ID
from troposphere import Output, AWS_REGION
from troposphere.ecr import Repository
from awacs.aws import Allow, Policy, AWSPrincipal, Statement
import awacs.ecr as ecr
import awacs.iam as iam

t = Template()
t.set_version('2010-09-09')

### -- Parameters
ECRRepoName = t.add_parameter(
    Parameter(
        "ECRRepoName",
        Type="String",
        Description="Name of the ECR Repository",
    )
)

IAMAllowedUser = t.add_parameter(
    Parameter(
        "IAMAllowedUser",
        Type="String",
        Description="IAM User",
    )
)

### -- Resources
ECRRepo = t.add_resource(
    Repository(
        'ECRRepo',
        RepositoryName=Ref("ECRRepoName"),
        RepositoryPolicyText=Policy(
            Version='2008-10-17',
            Statement=[
                Statement(
                    Sid='AllowPushPull',
                    Effect=Allow,
                    Principal=AWSPrincipal([
                        Join("", [
                            "arn:aws:iam::",
                            Ref(AWS_ACCOUNT_ID),
                            ":user/",
                            Ref("IAMAllowedUser"),
                        ]),
                    ]),
                    Action=[
                        ecr.GetDownloadUrlForLayer,
                        ecr.BatchGetImage,
                        ecr.BatchCheckLayerAvailability,
                        ecr.PutImage,
                        ecr.InitiateLayerUpload,
                        ecr.UploadLayerPart,
                        ecr.CompleteLayerUpload,
                    ],
                ),
            ]
        ),
    )
)

t.add_output(
    Output(
        "RepositoryURL",
        Description="The ECR repository URL",
        Value=Join("", [
            Ref(AWS_ACCOUNT_ID),
            ".dkr.ecr.",
            Ref(AWS_REGION),
            ".amazonaws.com/",
            Ref(ECRRepo),
        ]),
    )
)

### -- Print Template
f1 = open('./' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
