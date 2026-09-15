"""Bhashini translation service wrapper for Rural Advisor."""

from __future__ import annotations

import os
from dataclasses import dataclass

import requests
import httpx

PIPELINE_CONFIG_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
INFERENCE_TASK_TRANSLATION = "translation"
DEFAULT_PIPELINE_ID = "64392f96daac500b55c543cd"
SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"


@dataclass
class BhashiniCredentials:
    user_id: str
    api_key: str

    @classmethod
    def from_env(cls) -> "BhashiniCredentials":
        user_id = os.environ.get("BHASHINI_USER_ID")
        api_key = os.environ.get("BHASHINI_API_KEY")
        if not user_id or not api_key:
            raise RuntimeError(
                "Set BHASHINI_USER_ID and BHASHINI_API_KEY environment variables before calling the API."
            )
        return cls(user_id=user_id, api_key=api_key)


class BhashiniClient:
    def __init__(self, credentials: BhashiniCredentials | None = None):
        self.credentials = credentials or BhashiniCredentials.from_env()

    def _get_pipeline_config(
        self,
        task: str,
        source_lang: str,
        target_lang: str | None,
        pipeline_id: str = DEFAULT_PIPELINE_ID,
    ) -> dict:
        payload = {
            "pipelineTasks": [
                {
                    "taskType": task,
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            **({"targetLanguage": target_lang} if target_lang else {}),
                        }
                    },
                }
            ],
            "pipelineRequestConfig": {"pipelineId": pipeline_id},
        }
        headers = {
            "userID": self.credentials.user_id,
            "ulcaApiKey": self.credentials.api_key,
            "Content-Type": "application/json",
        }
        response = requests.post(PIPELINE_CONFIG_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def translate(self, text: str, source_lang: str = "en", target_lang: str = "hi") -> str:
        config = self._get_pipeline_config(INFERENCE_TASK_TRANSLATION, source_lang, target_lang)

        pipeline_response_config = config["pipelineResponseConfig"][0]
        service_id = pipeline_response_config["config"][0]["serviceId"]
        inference_endpoint = config["pipelineInferenceAPIEndPoint"]
        callback_url = inference_endpoint["callbackUrl"]
        auth_header_name = inference_endpoint["inferenceApiKey"]["name"]
        auth_header_value = inference_endpoint["inferenceApiKey"]["value"]

        compute_payload = {
            "pipelineTasks": [
                {
                    "taskType": INFERENCE_TASK_TRANSLATION,
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang,
                        },
                        "serviceId": service_id,
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        headers = {auth_header_name: auth_header_value, "Content-Type": "application/json"}

        response = requests.post(callback_url, json=compute_payload, headers=headers, timeout=15)
        response.raise_for_status()
        result = response.json()

        return result["pipelineResponse"][0]["output"][0]["target"]


def translate_text(text: str, source_language: str, target_language: str) -> str:
    return BhashiniClient().translate(text, source_lang=source_language, target_lang=target_language)


def transcribe_audio(audio: bytes) -> str:
    return ""


def synthesize_speech(text: str, language: str) -> bytes:
    return text.encode("utf-8")


def translate_with_sarvam(text: str, source_language: str, target_language: str) -> str:
    """Translate dynamic text without ever sending credentials to the client."""
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise RuntimeError("SARVAM_API_KEY is not configured")

    response = httpx.post(
        SARVAM_TRANSLATE_URL,
        headers={"api-subscription-key": api_key, "Content-Type": "application/json"},
        json={
            "input": text,
            "source_language_code": source_language,
            "target_language_code": target_language,
            "model": "mayura:v1",
        },
        timeout=20,
    )
    response.raise_for_status()
    translated = response.json().get("translated_text")
    if not translated:
        raise RuntimeError("Sarvam returned no translated text")
    return translated
