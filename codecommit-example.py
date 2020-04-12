import os

from troposphere import Parameter, Ref, Template
from troposphere.codecommit import Repository

t = Template()
t.set_version('2010-09-09')

### -- Parameters
RepoNameParam = t.add_parameter(
    Parameter(
        "RepoName",
        Type="String",
        Description="Name of a new Code Commit Repo"
    )
)

RepoDescriptionParam = t.add_parameter(
    Parameter(
        "RepoDescription",
        Type="String",
        Description="Description of a new Code Commit Repo"
    )
)

### -- Resources
Repo = t.add_resource(
    Repository(
        "Repo",
        RepositoryDescription=Ref("RepoDescription"),
        RepositoryName=Ref("RepoName")
    )
)

### -- Print Template
f1 = open('./' + (os.path.splitext(os.path.basename(__file__))[0]) + '.json', 'w+')
print(t.to_json(), file=f1)
print(t.to_json())
