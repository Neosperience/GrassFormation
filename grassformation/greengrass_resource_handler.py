# grassformation/greengrass_resource_handler.py

''' Defines the lambda functions for managing CloudFormation custom resources of
AWS Greengrass. '''

import botocore
from utils import change_requires_update, filter_dictionary

class CollectionHandler:
    ''' Instances of this class manages Greengrass CloudFormation resource
    requests.

    Currently supported resources:
    - FunctionDefinition
    - LoggerDefinition
    - ResourceDefinition
    - SubscriptionDefinition
    - DeviceDefinition
    - CoreDefinition
    '''

    def __init__(self, logger, resource_collection_key, id_key,
                 clean_resource_definition,
                 create_aws_function, create_version_aws_function,
                 update_aws_function, delete_aws_function, get_aws_function):
        '''
        Initializes the resource collection handler.

        Params:
          - logger (logging.Logger): The logger instance.
          - resource_collection_key (str): The key of the Greengrass resource
            collection in the CloudFormation resource definition
          - id_key (str): The key of the Greengrass resource id in update/delete
            requests
          - clean_resource_definition (func): The function that converts a
            single instance of a CloudFormation resource to a parameter set
            that can be passed to the AWS API.
          - create_aws_function (func): The Greengrass API function responsible
            for creating the resource definition.
          - create_version_aws_function (func): The Greengrass API function responsible
            for creating the resource definition version.
          - update_aws_function (func): The Greengrass API function responsible
            for updating the resource definition.
          - delete_aws_function (func): The Greengrass API function responsible
            for deleting the resource definition.
        '''
        self.logger = logger
        self.resource_collection_key = resource_collection_key
        self.id_key = id_key
        self.clean_resource_definition = clean_resource_definition
        self.create_aws_function = create_aws_function
        self.create_version_aws_function = create_version_aws_function
        self.update_aws_function = update_aws_function
        self.delete_aws_function = delete_aws_function
        self.get_aws_function = get_aws_function

    def clean_resource_definition_collection(self, resource_definition_collection):
        return [self.clean_resource_definition(res) for res in resource_definition_collection]

    def create(self, event, context):
        params = {}
        params['Name'] = event['ResourceProperties']['Name']
        initial_version = filter_dictionary(event['ResourceProperties'], [self.resource_collection_key])
        if initial_version:
            self.logger.info('Resource InitialVersion detected')
            params['InitialVersion'] = {
                self.resource_collection_key: self.clean_resource_definition_collection(initial_version[self.resource_collection_key])
            }
        response = self.create_aws_function(**params)
        response.pop('ResponseMetadata', None)
        physical_resource_id = response['Id']
        return physical_resource_id, response

    def get_current_definition(self, identifier):
        params = { self.id_key: identifier }
        response = self.get_aws_function(**params)
        response.pop('ResponseMetadata', None)
        return response

    def update(self, event, context):
        physical_resource_id = event['PhysicalResourceId']
        requires_new_version = self.resource_collection_key in event['ResourceProperties'] and \
                               change_requires_update(self.logger,
                                                      [self.resource_collection_key],
                                                      event['OldResourceProperties'],
                                                      event['ResourceProperties'])
        if requires_new_version:
            self.logger.info('Resource requires new version')
            params = filter_dictionary(event['ResourceProperties'], [self.resource_collection_key])
            params[self.resource_collection_key] = self.clean_resource_definition_collection(params[self.resource_collection_key])
            params[self.id_key] = physical_resource_id
            self.create_version_aws_function(**params)

        requires_rename = change_requires_update(self.logger,
                                                 ['Name'],
                                                 event['OldResourceProperties'],
                                                 event['ResourceProperties'])
        if requires_rename:
            self.logger.info('Resource is renamed')
            params = {
                self.id_key: physical_resource_id,
                'Name': event['ResourceProperties']['Name']
            }
            self.update_aws_function(**params)

        response = self.get_current_definition(physical_resource_id)
        return physical_resource_id, response

    def delete(self, event, context):
        physical_resource_id = event['PhysicalResourceId']
        if physical_resource_id == 'NONE':
            return
        try:
            params = { self.id_key: physical_resource_id }
            self.delete_aws_function(**params)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'IdNotFoundException':
                self.logger.warning('Requested to delete non existing resource.')
            else:
                raise e
        return
