import os

from troposphere import GetAtt, Output, Parameter, Ref, Template
from troposphere.iam import AccessKey, Group, LoginProfile, PolicyType
from troposphere.iam import User, UserToGroupAddition

t = Template()

t.set_description("Template to Create New Groups / Roles")

### -- Input Parameters
RoleParam = t.add_parameter(
    Parameter(
        "RoleParam",
        Type="String",
        Description="New IAM Role / Policy Name",
    )
)

GroupParam = t.add_parameter(
    Parameter(
        "GroupParam",
        Type="String",
        Description="New IAM Group Name",
    )
)

RegionParam = t.add_parameter(
    Parameter(
        "RegionParam",
        Type="String",
        Description="Region Constraint for IAM",
    )
)

### -- Resources
IAMGroup = t.add_resource(
    Group(
        "IAMGroup",
        GroupName=Ref(GroupParam),
    )
)

IAMPolicies = t.add_resource(
    PolicyType(
        "IAMPolicies",
        PolicyName=Ref(RoleParam),
        Groups=[Ref(GroupParam)],
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "ec2:*",
                    "s3:*",
                    "rds:*",
                    "elasticsearch:*",
                    "sqs:*",
                    "elasticache:*",
                    "events:DescribeRule",
                    "events:ListRuleNamesByTarget",
                    "events:ListRules",
                    "events:ListTargetsByRule",
                    "events:TestEventPattern",
                    "events:DescribeEventBus",
                    "kms:ListAliases",
                    "kms:DescribeKey",
                    "application-autoscaling:DescribeScalableTargets",
                    "application-autoscaling:DescribeScalingActivities",
                    "application-autoscaling:DescribeScalingPolicies",
                    "cloudwatch:DescribeAlarmHistory",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:DescribeAlarmsForMetric",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "datapipeline:DescribeObjects",
                    "datapipeline:DescribePipelines",
                    "datapipeline:GetPipelineDefinition",
                    "datapipeline:ListPipelines",
                    "datapipeline:QueryObjects",
                    "dynamodb:BatchGetItem",
                    "dynamodb:Describe*",
                    "dynamodb:List*",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dax:Describe*",
                    "dax:List*",
                    "dax:GetItem",
                    "dax:BatchGetItem",
                    "dax:Query",
                    "dax:Scan",
                    "iam:GetRole",
                    "iam:ListRoles",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTopics",
                    "lambda:ListFunctions",
                    "lambda:ListEventSourceMappings",
                    "lambda:GetFunctionConfiguration",
                    "resource-groups:ListGroups",
                    "resource-groups:ListGroupResources",
                    "resource-groups:GetGroup",
                    "resource-groups:GetGroupQuery",
                    "tag:GetResources"
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "aws:RequestedRegion": Ref(RegionParam)
                    }
                }
            }],
        },
        DependsOn=IAMGroup
    )
)

### -- Print Template
f1 = open('./' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
