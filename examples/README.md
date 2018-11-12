# GrassFormation examples

This folder contains usage examples of GrassFormation.

## `fullgrass.yaml`

This CloudFormation template shows you how to install, configure and link together the following Greengrass resources:

- Group
- CoreDefinition
- FunctionDefinition
- ResourceDefinition
- SubscriptionDefinition
- DeviceDefinition
- LoggerDefinition

### Deploying

Download [examples/fullgrass.yaml](examples/fullgrass.yaml) and head to the [CloudFormation management console](https://console.aws.amazon.com/cloudformation/home). Select "Create Stack" and upload the template file to S3. You will have to fill out the following stack parameters:

 - `GroupNameParameter`: The name of the Greengrass Group. All resources created by this template will be prefixed by this string.

 - `CSRParameter`: A Certificate Signing Request, created along with the certificates that you will deploy on your Greengrass Core. For more information check the [AWS IoT Documentation](https://docs.aws.amazon.com/iot/latest/apireference/API_CreateCertificateFromCsr.html). It should have the following format:

```
-----BEGIN CERTIFICATE REQUEST-----
[base64 encoded certificate request]
-----END CERTIFICATE REQUEST-----
```

The sample stack comes with a lambda function that will be deployed to the Greengrass Core device. The stack configures access to a simple hardware device (in this case `/dev/random`) and the lambda function shows you how to access this device. Two environment variables: `AWS_DEFAULT_REGION` and `HELLO` are also configured from the stack and accessed from the lambda. The lambda is running indefinitely and it periodically sends a random number picked up from `/dev/random` to CloudWatch and local file system logs so you can test the logger configuration.

### Stack outputs

This sample CloudFormation stack provides you with the following outputs:

| Output                                 | Description                                                               |
| -------------------------------------- | ------------------------------------------------------------------------- |
| CoreCertArn                            | The ARN of the Core Certificate                                           |
| CoreCertId                             | The ID of the Core Certificate                                            |
| CoreDefinitionArn                      | The ARN of the CoreDefinition                                             |
| CoreDefinitionId                       | The ID of the CoreDefinition                                              |
| CoreDefinitionLatestVersionArn         | The ARN of the latest version of CoreDefinition                           |
| CoreDefinitionLatestVersionId          | The ID of the latest version of CoreDefinition                            |
| CoreDefinitionName                     | The name of the CoreDefinition                                            |
| CorePolicyArn                          | The ARN of the Core Policy                                                |
| CorePolicyName                         | The name of the Core Policy                                               |
| CoreThingName                          | The name of the Core Thing                                                |
| FunctionDefinitionArn                  | The ARN of the FunctionDefinition                                         |
| FunctionDefinitionId                   | The ID of the FunctionDefinition                                          |
| FunctionDefinitionLatestVersionArn     | The ARN of the latest version of FunctionDefinition                       |
| FunctionDefinitionLatestVersionId      | The ID of the latest version of FunctionDefinition                        |
| FunctionDefinitionName                 | The name of the FunctionDefinition                                        |
| GreengrassGroupArn                     | The ARN of the GreengrassGroup                                            |
| GreengrassGroupId                      | The ID of the GreengrassGroup                                             |
| GreengrassGroupLatestVersionArn        | The ARN of the latest version of the GreengrassGroup                      |
| GreengrassGroupLatestVersionId         | The ID of the latest version of the GreengrassGroup                       |
| GreengrassGroupName                    | The name of the GreengrassGroup                                           |
| GreengrassGroupRoleArn                 | The ARN of the IAM Role of the Greengrass Group                           |
| GreengrassLambdaFullArn                | The fully qualified ARN of the lambda function running on Greengrass core |
| LoggerDefinitionArn                    | The ARN of the LoggerDefinition                                           |
| LoggerDefinitionId                     | The ID of the LoggerDefinition                                            |
| LoggerDefinitionLatestVersionArn       | The ARN of the latest version of LoggerDefinition                         |
| LoggerDefinitionLatestVersionId        | The ID of the latest version of LoggerDefinition                          |
| LoggerDefinitionName                   | The name of the LoggerDefinition                                          |
| ResourceDefinitionArn                  | The ARN of the ResourceDefinition                                         |
| ResourceDefinitionId                   | The ID of the ResourceDefinition                                          |
| ResourceDefinitionLatestVersionArn     | The ARN of the latest version of ResourceDefinition                       |
| ResourceDefinitionLatestVersionId      | The ID of the latest version of ResourceDefinition                        |
| ResourceDefinitionName                 | The name of the ResourceDefinition                                        |
| SubscriptionDefinitionArn              | The ARN of the SubscriptionDefinition                                     |
| SubscriptionDefinitionId               | The ID of the SubscriptionDefinition                                      |
| SubscriptionDefinitionLatestVersionArn | The ARN of the latest version of SubscriptionDefinition                   |
| SubscriptionDefinitionLatestVersionId  | The ID of the latest version of SubscriptionDefinition                    |
| SubscriptionDefinitionName             | The name of the SubscriptionDefinition                                    |

### Deleting

There is one glitch when you want to delete the sample CloudFormation stack. The `AWS::IoT::Certificate` type resource named `CoreCert` is left in `ACTIVATE` state after the deployment of the stack. This is necessary for the Greengrass Core to work. However this resource can not be deleted until it is not deactivated. So before starting the deletion of the stack you should deactivate it manually. Pick up the Physical ID of the `CoreCert` resource: you can find it under the "Resources" section of the details page of your deployed CloudFormation stack. Alternatively you can find the same ID in the "Outputs" section with `CoreCertId` key. Then call this command of the AWS cli:

```shell
aws iot update-certificate --certificate-id [Certificate ID] --new-status INACTIVE
```

Now you can delete the deployed stack.
