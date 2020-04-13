# Troposphere Examples for AWS Services

Example scripts to generate AWS Cloudformation Templates using Troposphere: https://github.com/cloudtools/troposphere

All scripts will output to json files as well as output the json to the screen when executing.

* **appstream-example.py** - Creates an AppStream 2.0 Stack / Fleet, the associated resources as well as one user.
* **appstream-image-builder-example.py** - Creates an AppStream 2.0 Image Builder.
* **aws-client-vpn-no-split-tunnel-example.py** - Creates an AWS Client VPN that routes all traffic over the VPN. Make sure to review all parameters before running.
* **aws-client-vpn-split-tunnel-example.py** - Creates an AWS Client VPN that only routes traffic destined for the VPC over the VPN. Make sure to review all parameters before running.
* **codecommit-example.py** - Creates a CodeCommit Repo.
* **ecr-example.py** - Creates an Elastic Container Repository along with allowing an IAM user access to the repo.
* **iam-role-policy-region-restriction-example.py** - Adds an IAM Policy / Group with a restriction by region.
* **waf** - WAF Example for Restricting ELB by IP Address. Make sure to modify the CSV File with the appropriate IPs.
