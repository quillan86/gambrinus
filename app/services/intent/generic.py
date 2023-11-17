import os
from typing import Tuple, Optional, Type
from abc import ABC, abstractmethod
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from langchain.base_language import BaseLanguageModel
from langchain.schema import BaseMessage


class GenericClassifierService(ABC):
    endpoint: str = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key: str = os.environ["AZURE_LANGUAGE_KEY"]
    project_name: str
    deployment_name: str

    def __init__(self):
        pass

    @classmethod
    def classify(cls, document: list[str]):
        """

        :param document:
        :return:
        """
        text_analytics_client = TextAnalyticsClient(
            endpoint=cls.endpoint,
            credential=AzureKeyCredential(cls.key),
        )

        poller = text_analytics_client.begin_single_label_classify(
            document,
            project_name=cls.project_name,
            deployment_name=cls.deployment_name
        )
        # get results
        document_results = poller.result()
        classification_result = list(document_results)[0]
        return classification_result

    @classmethod
    def predict(cls, doc: str) -> Tuple[str, float]:
        """
        Run the text classifier service for a given document.
        :param doc:
        :return:
        """
        document: list[str] = [doc]
        classification_result = cls.classify(document)

        if classification_result.kind == "CustomDocumentClassification":
            classification = classification_result.classifications[0]
            return classification.category, classification.confidence_score
        elif classification_result.is_error is True:
            raise ValueError("Document text '{}' has an error with code '{}' and message '{}'".format(
                doc, classification_result.error.code, classification_result.error.message
            ))
        else:
            # null value
            return '', 0.0


class LLMClassifierService(ABC):

    @classmethod
    @abstractmethod
    def classify(cls, query: str, chat_history: list[BaseMessage]):
        pass

    @classmethod
    @abstractmethod
    def predict(cls, query: str, chat_history: list[BaseMessage]):
        pass
