# GrassFormation

GrassFormation is a collection of AWS lambda functions that allows you to deploy Greengrass resources with CloudFormation that are otherwise not supported.

## Installing

Deploy the two lambda functions with [serverless](https://serverless.com/framework/docs/) framework. Note the Amazon Resources Names (ARNs) of the two functions. You can find them on the [AWS Lambda management console](https://console.aws.amazon.com/lambda/home).

Now you can start writing CloudFormation stacks that deploy Greengrass resources. An example template is provided in the `test/fullgrass.yaml` file.

## Deploying the sample CloudFormation stack

Pick up `test/fullgrass.yaml` and head to the [CloudFormation management console](https://console.aws.amazon.com/cloudformation/home). Select "Create Stack" and upload the template file to S3. You will have to fill out the following stack parameters:

 - `CSRParameter`: A Certificate Signing Request, created along with the certificates that you will deploy on your Greengrass Core. For more information check the [AWS IoT Documentation](https://docs.aws.amazon.com/iot/latest/apireference/API_CreateCertificateFromCsr.html). It should have the following format:

```
-----BEGIN CERTIFICATE REQUEST-----
[base64 encoded certificate request]
-----END CERTIFICATE REQUEST-----
```

 - `GFGroupLambda`: The ARN of lambda function responsible for creating `GrassFormation::Group` CloudFormation custom resources. You created this lambda function in the Installation step.
 - `GFCoreLambda`: The ARN of lambda function responsible for creating `GrassFormation::Core` CloudFormation custom resources. You created this lambda function in the Installation step.
 - `GFResourceLambda`: The ARN of lambda function responsible for creating `GrassFormation::Resource` CloudFormation custom resources. You created this lambda function in the Installation step.
 - `GroupNameParameter`: The name of the Greengrass Group.

## Deleting the sample CloudFormation stack

There is one glitch when you want to delete the sample CloudFormation stack. The `AWS::IoT::Certificate` type resource named `CoreCert` is left in `ACTIVATE` state after the deployment of the stack. This is necessary for the Greengrass Core to work. However this resource can not be deleted until it is not deactivated. So before starting the deletion of the stack you should deactivate it manually. Pick up the Physical ID of the `CoreCert` resource: you can find it under the "Resources" section of the details page of your deployed CloudFormation stack. Then call this command of the aws cli:

```
aws iot update-certificate --certificate-id [Physical ID from CF] --new-status INACTIVE
```

Now you can delete the deployed stack.

## Supported parameters

All custom resource lambdas pass most of their attributes to the appropriate AWS Greengrass API. However all functions abstract away the concept of "resource version" of Greengrass. Whenever you update your CloudFormation stack with GreenFormation, a new version of the updated entity will be automatically created. The attributes of the main entity (currently only `Name` for both entities) and those ones of the appropriate version entity are merged. Bearing this in mind you can find a list of the supported attributes below.

### GrassFormationGroup

Supported attributes:
 - `Name` (string): The name of the Greengrass Group
 - `CoreDefinitionVersionArn`, `DeviceDefinitionVersionArn`, `FunctionDefinitionVersionArn`, `SubscriptionDefinitionVersionArn`, `LoggerDefinitionVersionArn`, `ResourceDefinitionVersionArn`: see [Greengrass CreateGroupVersion API](https://docs.aws.amazon.com/greengrass/latest/apireference/creategroupversion-post.html) for more info.

### GrassFormationCore

Supported attributes:
 - `Name` (string): The name of the Greengrass Core
 - `Cores`: see [Greengrass CreateCoreDefinitionVersion API](https://docs.aws.amazon.com/greengrass/latest/apireference/createcoredefinitionversion-post.html) for more info.

### GrassFormationResource

Supported attributes:
 - `Name` (string): The name of the Greengrass Resources definition
 - `Resources`: see [Greengrass CreateResourceDefinitionVersion API](https://docs.aws.amazon.com/greengrass/latest/apireference/createresourcedefinitionversion-post.html) for more info.

## Returned values

Similarly to Supported Parameters, Group and Core custom resource lambda returns pretty much whatever the appropriate AWS API returns. You can find an example how to use them in the `GreengrassGroup` resource definition in th sample stack:

```
CoreDefinitionVersionArn: !GetAtt CoreDefinition.LatestVersionArn
```
