import os
import json
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


@dataclass
class Config:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    max_research_loops: int = int(os.getenv("MAX_RESEARCH_LOOPS", "2"))
    demo_mode: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

    @classmethod
    def reload(cls) -> "Config":
        load_dotenv(override=True)
        return cls()

    @property
    def active_provider(self) -> str:
        """Determines the active LLM provider based on settings and available keys."""
        if self.llm_provider in ("openai", "gemini"):
            return self.llm_provider
        if self.openai_api_key and not self.gemini_api_key:
            return "openai"
        if self.gemini_api_key:
            return "gemini"
        return "none"


config = Config()


def get_gemini_client():
    """Initializes Google GenAI Client if API key is present."""
    current_key = config.gemini_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    if not current_key:
        return None
    from google import genai
    return genai.Client(api_key=current_key)


def get_openai_client():
    """Initializes OpenAI Client if API key is present."""
    current_key = config.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    if not current_key:
        return None
    from openai import OpenAI
    return OpenAI(api_key=current_key)


def call_llm(
    prompt: str,
    system_instruction: Optional[str] = None,
    json_mode: bool = False,
    model: Optional[str] = None
) -> str:
    """
    Unified LLM invocation supporting both Google Gemini and OpenAI.
    Gracefully falls back to mock responses if no key is configured.
    """
    provider = config.active_provider

    # Route to OpenAI if selected or if OpenAI key is provided
    if provider == "openai":
        client = get_openai_client()
        if client:
            target_model = model or config.openai_model
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                params = {
                    "model": target_model,
                    "messages": messages,
                }
                if json_mode:
                    params["response_format"] = {"type": "json_object"}

                response = client.chat.completions.create(**params)
                return response.choices[0].message.content or ""
            except Exception as e:
                raise RuntimeError(f"Error calling OpenAI ({target_model}): {e}")

    # Route to Google Gemini
    if provider == "gemini" or config.gemini_api_key:
        client = get_gemini_client()
        if client:
            target_model = model or config.gemini_model
            try:
                from google.genai import types
                config_params = {}
                if system_instruction:
                    config_params["system_instruction"] = system_instruction
                if json_mode:
                    config_params["response_mime_type"] = "application/json"

                gen_config = types.GenerateContentConfig(**config_params) if config_params else None

                response = client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=gen_config,
                )
                return response.text or ""
            except Exception as e:
                if "not found" in str(e).lower() and target_model != "gemini-1.5-flash":
                    try:
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=prompt,
                        )
                        return response.text or ""
                    except Exception:
                        pass
                raise RuntimeError(f"Error calling Gemini ({target_model}): {e}")

    # Fallback simulation if no API keys are set yet
    if json_mode:
        return json.dumps({
            "message": "Demo Mode: Neither GEMINI_API_KEY nor OPENAI_API_KEY detected.",
            "sub_questions": [
                "What are the core architectural layers of the topic?",
                "What are the top real-world implementations and benchmarks?",
                "What are the major limitations and trade-offs?"
            ],
            "search_queries": [
                f"{prompt[:40]} architecture and framework",
                f"{prompt[:40]} benchmark comparison analysis",
                f"{prompt[:40]} challenges and production trade-offs"
            ],
            "claims": [
                {
                    "claim": "Modern agentic systems rely on multi-stage verification and specialized worker roles.",
                    "source_id": "S1",
                    "evidence_quote": "Multi-agent orchestration decouples search, verification, and synthesis.",
                    "category": "fact",
                    "confidence": "high"
                }
            ],
            "contradictions": [],
            "gaps": [],
            "needs_more_research": False,
            "new_search_queries": []
        })

    return (
        f"# Research Report: Topic Analysis\n\n"
        f"> **Notice**: Running in demonstration mode because no API key is set.\n"
        f"> To enable full live AI intelligence, add `GEMINI_API_KEY` or `OPENAI_API_KEY` to `.env`.\n\n"
        f"## Executive Summary\n"
        f"The research query was evaluated across gathered search sources.\n\n"
        f"## Findings\n"
        f"- The system successfully orchestrated the retrieval and extraction phases.\n"
        f"- Sourced evidence supports modular agent delegation [S1].\n\n"
        f"## References\n"
        f"- [S1] Verified Source Record"
    )
