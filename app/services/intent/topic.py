from .generic import GenericClassifierService


class TopicClassifierService(GenericClassifierService):
    project_name: str = 'gambrinus-topics'
    deployment_name: str = 'gambrinus-topic-model'
