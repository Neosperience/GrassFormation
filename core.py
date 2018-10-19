import crhelper
from utils import change_requires_update, filter_dictionary, val_to_bool

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

core_definition_version_attributes = ['Cores']

def clean_core(core):
    if 'SyncShadow' in core:
        core['SyncShadow'] = val_to_bool(core['SyncShadow'])
    return core

def clean_core_defs(core_defs):
    return {'Cores' : [clean_core(core) for core in core_defs['Cores']]}

def create(event, context):
    params = {}
    params['Name'] = event['ResourceProperties']['Name']
    initial_version = filter_dictionary(event['ResourceProperties'], core_definition_version_attributes)
    if initial_version:
        logger.info('Core InitialVersion detected')
        params['InitialVersion'] = clean_core_defs(initial_version)
    response = greengrass_client.create_core_definition(**params)
    response.pop('ResponseMetadata', None)
    physical_resource_id = response['Id']
    return physical_resource_id, response

def update(event, context):
    physical_resource_id = event['PhysicalResourceId']
    response = {}
    core_requires_new_version = change_requires_update(logger,
                                                       core_definition_version_attributes,
                                                       event['OldResourceProperties'],
                                                       event['ResourceProperties'])
    if core_requires_new_version:
        logger.info('Core requires new version')
        params = filter_dictionary(event['ResourceProperties'], core_definition_version_attributes)
        params['Cores'] = clean_core_defs(params)['Cores']
        params['CoreDefinitionId'] = physical_resource_id
        version_response = greengrass_client.create_core_definition_version(**params)
        version_response.pop('ResponseMetadata', None)
        response['Version'] = version_response

    core_requires_rename = change_requires_update(logger,
                                                  ['Name'],
                                                  event['OldResourceProperties'],
                                                  event['ResourceProperties'])
    if core_requires_rename:
        logger.info('Core is renamed')
        params = {
            'CoreDefinitionId': physical_resource_id,
            'Name': event['ResourceProperties']['Name']
        }
        greengrass_client.update_core_definition(**params)

    return physical_resource_id, response


def delete(event, context):
    physical_resource_id = event['PhysicalResourceId']
    if physical_resource_id == 'NONE':
        # This is a rollback from a failed create.  Nothing to do.
        return

    greengrass_client.delete_core_definition(CoreDefinitionId=physical_resource_id)
    return


def handler(event, context):
    # update the logger with event info
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, logger,
                                init_failed)
