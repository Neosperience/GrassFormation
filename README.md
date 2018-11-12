# GrassFormation

GrassFormation is a collection of [serverless](https://en.wikipedia.org/wiki/Serverless_computing) functions that you can install on your [Amazon Web Services](https://aws.amazon.com/what-is-aws/) (AWS) account. They enable you to easily provision [AWS IoT](https://aws.amazon.com/iot/), specifically Greengrass resources on your account in a reproducible, controlled way.

[Greengrass](https://aws.amazon.com/greengrass/) is a software solution of AWS that allows you to remotely provision software code and device configuration on IoT devices. At the time there are three ways to use Greengrass: from the [AWS Management Console](https://console.aws.amazon.com/iot/home#/greengrassIntro), programmatically from one of the [AWS SDKs](https://aws.amazon.com/tools/#sdk) or by using [AWS Command Line Interface](https://aws.amazon.com/cli/) (CLI). The first method works well for prototyping but does not allow you to create a reliable, reproducible, production ready deployment pipeline. The second and the third method are extremely tedious and error prone considering the complexity of the [Greengrass data model](https://read.acloud.guru/aws-greengrass-the-missing-manual-2ac8df2fbdf4#ad8d). The standard way to create cloud infrastructure in a reproducible, testable and automatic way on AWS infrastructure is to use [CloudFormation](https://aws.amazon.com/cloudformation/) templates. Unfortunately at the time there is no support for Greengrass resources in CloudFormation. GrassFormation aims to remedy this shortcoming.

GrassFormation is a collection of [AWS lambda](https://aws.amazon.com/lambda/) functions and a CloudFormation [transform macro](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-macros.html) that allows you to deploy resources with CloudFormation that are otherwise not supported. After installing GrassFormation you can provision for example a Greengrass Group together with your other resources from a CloudFormation template as simple as:

```yaml
AWSTemplateFormatVersion: '2010-09-09'

# Add GrassFormation to the transform section of your template:
Transform: ['AWS::Serverless-2016-10-31', 'GrassFormation']

GreengrassGroup:
  # GrassFormation defines new template types:
  Type: NSP::GrassFormation::Group
  Properties:
    Name: !Ref GroupNameParameter
    # Refer to other resources required by the Group in the standard CF way:
    GroupRoleArn: !GetAtt GreengrassGroupRole.Arn
    CoreDefinitionVersionArn: !GetAtt CoreDefinition.LatestVersionArn
    ResourceDefinitionVersionArn: !GetAtt ResourceDefinition.LatestVersionArn
    LoggerDefinitionVersionArn: !GetAtt LoggerDefinition.LatestVersionArn
    SubscriptionDefinitionVersionArn: !GetAtt SubscriptionDefinition.LatestVersionArn
    FunctionDefinitionVersionArn: !GetAtt FunctionDefinition.LatestVersionArn
```

For more examples see the [examples](examples) folder.

## Installing

### Prerequisites

You will need an [AWS Account](https://aws.amazon.com).

### Automatic installation

A packaged CloudFormation template is provided for you for easy, on-click installation of GrassFormation. This is the recommended method. This template will install some lambda functions to handle Greengrass resources creation requests, and the macro definition to easily integrate the resources into your stack. When you are ready, click on the button bellow:

[![Install GrassFormation to your AWS account](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=GrassFormation&templateURL=https://s3.amazonaws.com/sam-packages.neosperience.com/GrassFormation/template.yaml)

On the CloudFormation Management Console click three times "Next", acknowledge the creation of the IAM role (they are the lambda function execution roles) and finally "Create". When the stack finished the deployment you can start writing CloudFormation stacks that deploy Greengrass resources.

This template installs exclusively pay per use lambda resources on your account. AWS provides a generous [free tier](https://aws.amazon.com/free/) and generally low cost for lambda functions.

### Manual installation

Use this method if you're familiar with [Serverless Application Model](https://github.com/awslabs/serverless-application-model) and want to have full control over the installation.

This project supports [Serverless Application Model](https://github.com/awslabs/serverless-application-model). To deploy the CloudFormation custom resource handler lambda functions and the transform macro to your AWS infrastructure you should have:
 - An AWS account with an IAM user that has administrator permissions.
 - The AWS CLI (command line interface) installed.
 - To be able to use the local testing functionalities, also AWS SAM CLI installed.

A Makefile is provided for your convenience. To deploy the stack with make you should pass an s3 bucket name where the packaged SAM application will be deployed and optionally set the AWS region of the deployment (defaults to us-east-1). These variables can be also set as shell environment variables.

```
$ make deploy SAM_S3_BUCKET=my-bucket AWS_DEFAULT_REGION=eu-west-1
```

Now you can start writing CloudFormation stacks that deploy Greengrass resources. Examples are provided in the [examples](examples) folder.

## Usage

After installing this stack on your account you can start creating Greengrass resources in your CloudFormation template. First you should define the `GrassFormation` transform in your template:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: GrassFormation
```

Now you can start using the following new resource types:

 - `NSP::GrassFormation::Group`
 - `NSP::GrassFormation::Core`
 - `NSP::GrassFormation::Function`
 - `NSP::GrassFormation::Resource`
 - `NSP::GrassFormation::Subscription`
 - `NSP::GrassFormation::Device`
 - `NSP::GrassFormation::Logger`

All custom resource handler lambdas pass most of their attributes to the appropriate [AWS Greengrass API](https://docs.aws.amazon.com/greengrass/latest/apireference/api-actions.html) However all functions abstract away the concept of "resource definition version" of Greengrass. Whenever you update your CloudFormation stack with GreenFormation, a new version of the updated entity will be automatically created. The attributes of the main entity (currently only `Name` for both entities) and those ones of the appropriate version entity are merged. Bearing this in mind you can find a list of the supported attributes below.

### NSP::GrassFormation::Group

Supported attributes:
 - `Name` (string): The name of the Greengrass Group
 - `GroupRoleArn` (string): The ARN of the IAM Role to be associated with the Group. Your AWS Greengrass core will use the role to access AWS cloud services. The role's permissions should allow Greengrass core Lambda functions to perform actions against the cloud. The ARN specified in this attribute will be passed to the [AssociateRoleToGroup](https://docs.aws.amazon.com/greengrass/latest/apireference/associateroletogroup-put.html) API.
 - `CoreDefinitionVersionArn`, `DeviceDefinitionVersionArn`, `FunctionDefinitionVersionArn`, `SubscriptionDefinitionVersionArn`, `LoggerDefinitionVersionArn`, `ResourceDefinitionVersionArn`: see [CreateGroupVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/creategroupversion-post.html) API for more info.

### NSP::GrassFormation::Core

Supported attributes:
 - `Name` (string): The name of the Greengrass Core
 - `Cores`: see [CreateCoreDefinitionVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/createcoredefinitionversion-post.html) API for more info.

### NSP::GrassFormation::Function

Supported attributes:
 - `Name` (string): The name of the Greengrass Function Definition
 - `Functions`: see [CreateFunctionDefinitionVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/createfunctiondefinitionversion-post.html) API for more info.

### NSP::GrassFormation::Resource

Supported attributes:
 - `Name`: string. The name of the Greengrass Resources Definition
 - `Resources`: see [CreateResourceDefinitionVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/createresourcedefinitionversion-post.html) API for more info.

### NSP::GrassFormation::Subscription

Supported attributes:
 - `Name`: string. The name of the Greengrass Subscription Definition
 - `Subscriptions`: see [CreateSubscriptionDefinitionVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/createsubscriptiondefinitionversion-post.html) API for more info.

### NSP::GrassFormation::Device

Supported attributes:
 - `Name`: string. The name of the Greengrass Device Definition
 - `Devices`: see [CreateDeviceDefinitionVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/createdevicedefinitionversion-post.html) API for more info.

### NSP::GrassFormation::Logger

Supported attributes:
 - `Name`: string. The name of the Greengrass Device Definition
 - `Loggers`: see [CreateLoggerDefinitionVersion](https://docs.aws.amazon.com/greengrass/latest/apireference/createloggerdefinitionversion-post.html) API for more info.

## Returned values

Similarly to Supported Parameters, the custom resource lambda functions return pretty much whatever the appropriate AWS API returns. For all Greengrass resources managed by GrassFormation the return value has the following schema:

 - `Name` : string. The name of the resource definition.
 - `Id`: string. The ID of the resource definition.
 - `Arn`: string. The ARN of the resource definition.
 - `LatestVersion`: string. The ID of the latest version of resourource definition.
 - `LatestVersionArn`: string. The ARN of the latest version of resourource definition.

You can find an example how to use them in the `GreengrassGroup` resource definition in the sample stack:

```yaml
CoreDefinitionVersionArn: !GetAtt CoreDefinition.LatestVersionArn
```
