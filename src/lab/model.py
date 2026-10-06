"""PROVIDED - do not edit. Builds the chat model from environment variables (see .env.example).

Four configurations are supported (the first that matches wins):

1. ModelAPI/OpenAI-compatible endpoint - set:
   MODELAPI_API_KEY, MODELAPI_MODEL
   (optional: MODELAPI_BASE_URL, defaults to https://modelapi.vn/v1).
2. NVIDIA NIM/OpenAI-compatible endpoint - set:
   NVIDIA_API_KEY, NVIDIA_MODEL
   (optional: NVIDIA_BASE_URL, defaults to https://integrate.api.nvidia.com/v1).
3. Azure OpenAI or an OpenAI-compatible gateway - set all three variables:
   AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_MODEL
   (optional: AZURE_OPENAI_API_VERSION, used only for real Azure endpoints).
4. Any LangChain provider - set LAB_MODEL="<provider>:<model>" (default "deepseek:deepseek-chat")
   and the key variable of that provider (for example DEEPSEEK_API_KEY).
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


def make_model():
    """Return a chat model configured from the environment."""
    temperature = float(os.getenv("LAB_TEMPERATURE", "0"))
    modelapi_key = os.getenv("MODELAPI_API_KEY") or os.getenv("CODEX_API_KEY")
    if modelapi_key:
        from langchain_openai import ChatOpenAI
        kwargs = {}
        if os.getenv("MODELAPI_MAX_TOKENS"):
            kwargs["max_tokens"] = int(os.environ["MODELAPI_MAX_TOKENS"])
        return ChatOpenAI(
            base_url=os.getenv("MODELAPI_BASE_URL", "https://modelapi.vn/v1"),
            api_key=modelapi_key,
            model=os.getenv("MODELAPI_MODEL", "gpt-6.1-sol"),
            temperature=temperature,
            top_p=float(os.getenv("MODELAPI_TOP_P", "1")),
            timeout=float(os.getenv("MODELAPI_TIMEOUT", "60")),
            max_retries=int(os.getenv("MODELAPI_MAX_RETRIES", "1")),
            **kwargs,
        )

    nvidia_key = os.getenv("NVIDIA_API_KEY")
    nvidia_model = os.getenv("NVIDIA_MODEL")
    if nvidia_key:
        from langchain_openai import ChatOpenAI
        kwargs = {}
        if os.getenv("NVIDIA_MAX_TOKENS"):
            kwargs["max_tokens"] = int(os.environ["NVIDIA_MAX_TOKENS"])
        return ChatOpenAI(
            base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            api_key=nvidia_key,
            model=nvidia_model or "deepseek-ai/deepseek-v4.1-flash",
            temperature=temperature,
            top_p=float(os.getenv("NVIDIA_TOP_P", "0.95")),
            timeout=float(os.getenv("NVIDIA_TIMEOUT", "45")),
            max_retries=int(os.getenv("NVIDIA_MAX_RETRIES", "0")),
            **kwargs,
        )

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_MODEL")
    if endpoint and key and deployment:
        if "openai.azure.com" in endpoint or "cognitiveservices.azure.com" in endpoint:
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                azure_endpoint=endpoint, api_key=key, azure_deployment=deployment,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                temperature=temperature, timeout=120,
            )
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(base_url=endpoint, api_key=key, model=deployment, temperature=temperature, timeout=120)
    return init_chat_model(os.getenv("LAB_MODEL", "deepseek:deepseek-chat"), temperature=temperature)
