from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output, If, And, Not, Or, Equals, Condition
from troposphere import Parameter, Ref, Tags, Template
from troposphere.wafregional import WebACL
from troposphere.wafregional import Rule
from troposphere.wafregional import IPSet
from troposphere.wafregional import WebACLAssociation
from troposphere.wafregional import *
import os
import csv

t = Template()

t.set_version("2010-09-09")

t.set_description("""\
Custom WAF using a list of IP addresses for access.""")

## -- Parameters
ELBARN = t.add_parameter(
    Parameter(
        "ELBARN",
        Type="String",
        Description="ARN of the ELB to associate with the WAF"
    )
)

## -- Resources
WAFWebACL = t.add_resource(
    WebACL(
        "WAFWebACL",
        DefaultAction=Action(Type="BLOCK"),
        Rules=[Rules(Action=Action(Type="ALLOW"),Priority=1,RuleId=Ref("WAFRule1"))],
        Name="WAFWebACL",
        MetricName="WAFWebACL",
    )
)

WAFRule1 = t.add_resource(
    Rule(
        "WAFRule1",
        Predicates=[Predicates(DataId=Ref("Whitelist1"),Type="IPMatch",Negated="false")],
        Name="WAFRule1",
        MetricName="WAFRule1",
    )
)

whitelist = []
with open('./WAF_IP_Whitelist.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        TIPSetDescriptors=IPSetDescriptors(Type="IPV4", Value=row["Cidr"])
        whitelist.append(TIPSetDescriptors)
    #print(TIPSetDescriptors)

Whitelist1 = t.add_resource(IPSet(
    "Whitelist1",
    Name="Whitelist1",
    IPSetDescriptors=whitelist,
))

WAFELBAssociation = t.add_resource(WebACLAssociation(
    "WAFELBAssociation",
    ResourceArn=Ref("ELBARN"),
    WebACLId=Ref("WAFWebACL")
))

# Print CloudFormation Template
f1 = open('./' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
