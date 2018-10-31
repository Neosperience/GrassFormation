# grassformation/index.py

''' Defines the lambda functions for managing CloudFormation custom resources of
AWS Greengrass. '''

import botocore
from grassformation.utils import crhelper
from grassformation.utils import keypath
from grassformation.utils import change_requires_update, filter_dictionary, val_to_bool
from grassformation.greengrass_resource_handler import CollectionHandler

# initialise logger
logger = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
logger.info('Logging configured')
# set global to track init failures
init_failed = False

try:
    import boto3
    greengrass_client = boto3.client('greengrass')
    logger.info("Container initialization completed")
except Exception as e:
    logger.error(e, exc_info=True)
    init_failed = e

def core_handler(event, context):
    ''' Lambda handler to manage AWS Greengrass CoreDefinition resources. '''
    global logger
    logger = crhelper.log_config(event)

    def clean_core(core):
        return keypath.replace(core, 'SyncShadow', lambda e: val_to_bool(e), inline=False)

    handler = CollectionHandler(
                    logger, 'Cores', 'CoreDefinitionId',
                    clean_core,
                    greengrass_client.create_core_definition,
                    greengrass_client.create_core_definition_version,
                    greengrass_client.update_core_definition,
                    greengrass_client.delete_core_definition,
                    greengrass_client.get_core_definition
               )

    return crhelper.cfn_handler(event, context,
                                handler.create, handler.update, handler.delete,
                                logger, init_failed)

def function_handler(event, context):
    ''' Lambda handler to manage AWS Greengrass FunctionDefinition resources. '''
    global logger
    logger = crhelper.log_config(event)

    def clean_func(function):
        res = function
        res = keypath.replace(res, 'FunctionConfiguration.Environment.AccessSysfs',
                              lambda e: val_to_bool(e), inline=False)
        res = keypath.replace(res, 'FunctionConfiguration.Pinned',
                              lambda e: val_to_bool(e), inline=False)
        res = keypath.replace(res, 'FunctionConfiguration.MemorySize',
                              lambda e: int(e), inline=False)
        res = keypath.replace(res, 'FunctionConfiguration.Timeout',
                              lambda e: int(e), inline=False)
        return res

    handler = CollectionHandler(
                    logger, 'Functions', 'FunctionDefinitionId',
                    clean_func,
                    greengrass_client.create_function_definition,
                    greengrass_client.create_function_definition_version,
                    greengrass_client.update_function_definition,
                    greengrass_client.delete_function_definition,
                    greengrass_client.get_function_definition
               )

    return crhelper.cfn_handler(event, context,
                                handler.create, handler.update, handler.delete,
                                logger, init_failed)

def logger_handler(event, context):
    ''' Lambda handler to manage AWS Greengrass LoggerDefinition resources. '''
    global logger
    logger = crhelper.log_config(event)

    def clean_logger(logger_def):
        return keypath.replace(logger_def, 'Space', lambda e: int(e), inline=False)

    handler = CollectionHandler(
                    logger, 'Loggers', 'LoggerDefinitionId',
                    clean_logger,
                    greengrass_client.create_logger_definition,
                    greengrass_client.create_logger_definition_version,
                    greengrass_client.update_logger_definition,
                    greengrass_client.delete_logger_definition,
                    greengrass_client.get_logger_definition
               )

    return crhelper.cfn_handler(event, context,
                                handler.create, handler.update, handler.delete,
                                logger, init_failed)

def resource_handler(event, context):
    ''' Lambda handler to manage AWS Greengrass ResourceDefinition resources. '''
    global logger
    logger = crhelper.log_config(event)

    def clean_res(resource):
        res = resource
        res = keypath.replace(res,
                              'ResourceDataContainer.LocalDeviceResourceData.GroupOwnerSetting.AutoAddGroupOwner',
                              lambda e: val_to_bool(e),
                              inline=False)
        res = keypath.replace(res,
                              'ResourceDataContainer.LocalVolumeResourceData.GroupOwnerSetting.AutoAddGroupOwner',
                              lambda e: val_to_bool(e),
                              inline=False)
        return res

    handler = CollectionHandler(
                    logger, 'Resources', 'ResourceDefinitionId',
                    clean_res,
                    greengrass_client.create_resource_definition,
                    greengrass_client.create_resource_definition_version,
                    greengrass_client.update_resource_definition,
                    greengrass_client.delete_resource_definition,
                    greengrass_client.get_resource_definition
               )

    return crhelper.cfn_handler(event, context,
                                handler.create, handler.update, handler.delete,
                                logger, init_failed)

def subscription_handler(event, context):
    ''' Lambda handler to manage AWS Greengrass SubscriptionDefinition resources. '''
    global logger
    logger = crhelper.log_config(event)

    def clean_sub(subscription):
        return subscription

    handler = CollectionHandler(
                    logger, 'Subscriptions', 'SubscriptionDefinitionId',
                    clean_sub,
                    greengrass_client.create_subscription_definition,
                    greengrass_client.create_subscription_definition_version,
                    greengrass_client.update_subscription_definition,
                    greengrass_client.delete_subscription_definition,
                    greengrass_client.get_subscription_definition
               )

    return crhelper.cfn_handler(event, context,
                                handler.create, handler.update, handler.delete,
                                logger, init_failed)

def device_handler(event, context):
    ''' Lambda handler to manage AWS Greengrass DeviceDefinition resources. '''
    global logger
    logger = crhelper.log_config(event)

    def clean_device(device):
        return keypath.replace(device, 'SyncShadow', lambda e: val_to_bool(e), inline=False)

    handler = CollectionHandler(
                    logger, 'Devices', 'DeviceDefinitionId',
                    clean_core,
                    greengrass_client.create_device_definition,
                    greengrass_client.create_device_definition_version,
                    greengrass_client.update_device_definition,
                    greengrass_client.delete_device_definition,
                    greengrass_client.get_device_definition
               )

    return crhelper.cfn_handler(event, context,
                                handler.create, handler.update, handler.delete,
                                logger, init_failed)
