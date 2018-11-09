# GrassFormation

GrassFormation is a collection of AWS lambda functions and a CloudFormation transform macro that allows you to deploy Greengrass resources with CloudFormation that are otherwise not supported.

## Installing

### Automatic installation

A packaged CloudFormation template is provided for you for easy, on-click installation of GrassFormation. This is the recommended method. This template will install some lambda functions to handle Greengrass resources creation requests, and the macro definition to easily integrate the resources into your stack. When you are ready, click on the button bellow:

[![Install GrassFormation to your account](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=GrassFormation&templateURL=https://s3.amazonaws.com/sam-packages.neosperience.com/GrassFormation/template.yaml)

On the CloudFormation Management Console click three times "Next", acknowledge the creation of the IAM role (they are the lambda function execution roles) and finally "Create". When the stack finished the deployment you can start writing CloudFormation stacks that deploy Greengrass resources. An example template is provided in the `examples/fullgrass.yaml` file.

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

Now you can start writing CloudFormation stacks that deploy Greengrass resources. An example template is provided in the `examples/fullgrass.yaml` file.

## Deploying the sample CloudFormation stack

Pick up `examples/fullgrass.yaml` and head to the [CloudFormation management console](https://console.aws.amazon.com/cloudformation/home). Select "Create Stack" and upload the template file to S3. You will have to fill out the following stack parameters:

 - `CSRParameter`: A Certificate Signing Request, created along with the certificates that you will deploy on your Greengrass Core. For more information check the [AWS IoT Documentation](https://docs.aws.amazon.com/iot/latest/apireference/API_CreateCertificateFromCsr.html). It should have the following format:

```
-----BEGIN CERTIFICATE REQUEST-----
[base64 encoded certificate request]
-----END CERTIFICATE REQUEST-----
```

 - `GroupNameParameter`: The name of the Greengrass Group.

The sample stack comes with a lambda function that will be deployed to the Greengrass Core device. The stack configures access to a simple hardware device (in this case `/dev/random`) and the lambda function shows you how to access this device. Two environment variables: `AWS_DEFAULT_REGION` and `HELLO` are also configured from the stack and accessed from the lambda. The lambda is running indefinitely and it periodically sends a random number picked up from `/dev/random` to CloudWatch and local file system logs so you can test the logger configuration.

## Deleting the sample CloudFormation stack

There is one glitch when you want to delete the sample CloudFormation stack. The `AWS::IoT::Certificate` type resource named `CoreCert` is left in `ACTIVATE` state after the deployment of the stack. This is necessary for the Greengrass Core to work. However this resource can not be deleted until it is not deactivated. So before starting the deletion of the stack you should deactivate it manually. Pick up the Physical ID of the `CoreCert` resource: you can find it under the "Resources" section of the details page of your deployed CloudFormation stack. Then call this command of the aws cli:

```shell
aws iot update-certificate --certificate-id [Physical ID from CF] --new-status INACTIVE
```

Now you can delete the deployed stack.

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
