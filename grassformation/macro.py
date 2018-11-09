# KinesisVideoFormation/src/macro.py

''' Defines the lambda function CloudFormation macro transfor of
NSP::GrassFormation resources. '''

import botocore
import os
from utils import crhelper

# initialise logger
logger = crhelper.log_config({'RequestId': 'CONTAINER_INIT'})
logger.info('Logging configured')
# set global to track init failures
init_failed = False

try:
    DISPATCH_HANDLER_LAMBDA_ARN = os.environ['DISPATCH_HANDLER_LAMBDA_ARN']
    logger.info('Container initialization completed')
except Exception as e:
    logger.error(e, exc_info=True)
    init_failed = e

def create_response(event, success, result):
    return {
        'requestId': event['requestId'],
        'status': 'success' if success else 'failure',
        'fragment': result if success else event['fragment']
    }

RESOURCE_TYPE_PREFIX = 'NSP::GrassFormation::'

def handle_template(request_id, template):
    new_resources = {}

    for name, resource in template.get('Resources', {}).items():
        resource_type = resource['Type']
        if resource_type.startswith(RESOURCE_TYPE_PREFIX):
            gf_resource_type = resource_type.split('::')[-1]
            props = resource['Properties']
            props['ServiceToken'] = DISPATCH_HANDLER_LAMBDA_ARN
            props['GrassFormationResourceType'] = gf_resource_type
            new_resources[name] = {
                'Type': 'Custom::GrassFormation{}'.format(gf_resource_type),
                'Version': '1.0',
                'Properties': props
            }

    for name, resource in new_resources.items():
        template['Resources'][name] = resource

    return template

def handler(event, context):
    # update the logger with event info
    global logger
    logger = crhelper.log_config({'RequestId': event['requestId']})
    try:
        result = handle_template(event['requestId'], event['fragment'])
    except Exception as e:
        logger.error(e, exc_info=True)
        return create_response(event, False, None)
    else:
        return create_response(event, True, result)
