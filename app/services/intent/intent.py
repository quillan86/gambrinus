from .generic import GenericClassifierService


class IntentClassifierService(GenericClassifierService):
    project_name: str = 'gambrinus-intents'
    deployment_name: str = 'gambrinus-intent-model'
