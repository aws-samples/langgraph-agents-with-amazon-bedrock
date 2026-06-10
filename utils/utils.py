import logging
import os
import json
import pprint
from typing import Optional

import boto3


def set_logger(log_level: str = "INFO") -> object:
    log_level = os.environ.get("LOG_LEVEL", log_level).strip().upper()
    logging.basicConfig(
        format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger


logger = set_logger()


def set_pretty_printer():
    return pprint.PrettyPrinter(indent=2, width=100)


def get_tavily_api(key: str, region_name: Optional[str] = None) -> Optional[str]:
    """Return the Tavily API key from the environment or AWS Secrets Manager.

    Looks for ``key`` first in the environment (typically sourced from a local
    ``.env`` file) and, if the value is missing or is still the placeholder from
    ``env.tmp``, falls back to reading a secret with the same name from AWS
    Secrets Manager in ``region_name``.

    Returns:
        The Tavily API key, or ``None`` if no key could be found. Previous
        versions of this helper raised an exception in that case, which blocked
        every lab before any LangGraph content could be reached. Returning
        ``None`` lets callers decide whether to continue (Labs 2, 4, and 5 can
        fall back to DuckDuckGo; Labs 3 and 6 still require Tavily). See
        ``get_search_tool`` for a drop-in replacement that handles this.
    """

    tavily_api_prefix = "tvly-"
    env_value = os.environ.get(key)

    if env_value and env_value.startswith(tavily_api_prefix):
        logger.info(f"{key} variable correctly retrieved from the .env file.")
        return env_value

    if env_value:
        logger.info(
            f'{key} value in the environment does not start with "{tavily_api_prefix}" '
            f'(got "{env_value[:5]}..."). Trying AWS Secrets Manager.'
        )
    else:
        logger.info(
            f"{key} not set in the environment. Trying AWS Secrets Manager."
        )

    if region_name is None:
        region_name = os.environ.get("AWS_REGION", "us-east-1")

    try:
        session = boto3.session.Session()
        secrets_manager = session.client(
            service_name="secretsmanager", region_name=region_name
        )
        secret_value = secrets_manager.get_secret_value(SecretId=key)
        secret_string = secret_value["SecretString"]
        secret = json.loads(secret_string).get(key)
    except Exception as e:
        logger.warning(
            f"{key} could not be retrieved from AWS Secrets Manager either "
            f"({type(e).__name__}: {e}). Tavily-based labs will not run. "
            f"Labs 2, 4, and 5 can still run via the DuckDuckGo fallback "
            f"exposed by utils.get_search_tool()."
        )
        return None

    if secret and secret.startswith(tavily_api_prefix):
        logger.info(f"{key} variable correctly retrieved from AWS Secrets Manager.")
        os.environ[key] = secret
        return secret

    logger.warning(
        f"{key} retrieved from AWS Secrets Manager does not start with "
        f'"{tavily_api_prefix}". Tavily-based labs will not run.'
    )
    return None


def get_search_tool(max_results: int = 2, region_name: Optional[str] = None):
    """Return a LangChain web-search tool.

    If a valid Tavily API key is configured (via ``TAVILY_API_KEY`` in the
    environment or in AWS Secrets Manager), returns a Tavily-backed tool. This
    matches the default workshop experience.

    If no Tavily key is available, returns a DuckDuckGo-backed tool instead.
    The DuckDuckGo fallback is a drop-in replacement for Labs 2, 4, and 5 —
    wire it into your LangGraph agent the same way you would wire the Tavily
    tool. Lab 3 demonstrates Tavily's agentic capabilities specifically and
    is not a clean DuckDuckGo swap; Lab 6 uses ``TavilyClient.search()``
    directly and also requires a Tavily key.

    Args:
        max_results: Maximum number of search results to return.
        region_name: AWS Region for Secrets Manager lookup of the Tavily key.

    Returns:
        A ``langchain_core.tools.BaseTool`` instance — either
        ``langchain_tavily.TavilySearch`` (preferred) or
        ``langchain_community.tools.DuckDuckGoSearchResults`` (fallback).
    """

    tavily_key = get_tavily_api("TAVILY_API_KEY", region_name=region_name)

    if tavily_key:
        # TavilySearch reads TAVILY_API_KEY from the environment; get_tavily_api
        # already placed it there if it came from Secrets Manager.
        from langchain_tavily import TavilySearch

        logger.info("get_search_tool: using Tavily.")
        return TavilySearch(max_results=max_results)

    from langchain_community.tools import DuckDuckGoSearchResults

    logger.info(
        "get_search_tool: no Tavily key found; falling back to DuckDuckGo. "
        "Labs 3 and 6 still require Tavily."
    )
    return DuckDuckGoSearchResults(max_results=max_results, output_format="list")
