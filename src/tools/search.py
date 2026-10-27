import re
import urllib.parse
from typing import List, Dict, Any, Optional
from src.config import config


def normalize_url(raw_url: str) -> str:
    """Removes trailing slashes, fragments, and tracking parameters."""
    try:
        parsed = urllib.parse.urlparse(raw_url)
        # Reconstruct without query tracking params or fragments
        clean_path = parsed.path.rstrip("/")
        clean_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}"
        return clean_url.lower()
    except Exception:
        return raw_url.strip().lower()


def extract_domain(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return ""


def search_tavily(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Performs search using official Tavily API client."""
    if not config.tavily_api_key:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=config.tavily_api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=False
        )
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "published_date": item.get("published_date")
            })
        return results
    except Exception as e:
        print(f"[Search Tool Warning] Tavily search failed ({e}), falling back to DuckDuckGo.")
        return []


def search_duckduckgo(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Performs web search via DDGS fallback (no API key required)."""
    try:
        from ddgs import DDGS
        ddgs = DDGS()
        raw_results = list(ddgs.text(query, max_results=max_results))
        results = []
        for item in raw_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
                "published_date": None
            })
        return results
    except Exception as e:
        print(f"[Search Tool Warning] DuckDuckGo search failed: {e}")
        return []


def search_web_queries(
    queries: List[str],
    max_results_per_query: int = 4,
    existing_sources: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Executes multiple search queries, deduplicates by URL and domain,
    and returns a merged dictionary of indexed source cards:
    { "S1": { "id": "S1", "title": "...", "url": "...", "snippet": "..." } }
    """
    sources_dict = dict(existing_sources or {})
    known_urls = {normalize_url(s["url"]) for s in sources_dict.values() if "url" in s}

    # Determine next available sequential ID index
    existing_indices = []
    for k in sources_dict.keys():
        match = re.search(r"\d+", k)
        if match:
            existing_indices.append(int(match.group()))
    next_idx = (max(existing_indices) + 1) if existing_indices else 1

    for q in queries:
        cleaned_q = q.strip()
        if not cleaned_q:
            continue

        # Try Tavily first if key is available; otherwise fallback to DDGS
        items = []
        if config.tavily_api_key:
            items = search_tavily(cleaned_q, max_results=max_results_per_query)
        
        if not items:
            items = search_duckduckgo(cleaned_q, max_results=max_results_per_query)

        for item in items:
            url = item.get("url", "").strip()
            if not url:
                continue

            norm_url = normalize_url(url)
            if norm_url in known_urls:
                continue

            known_urls.add(norm_url)
            source_id = f"S{next_idx}"
            next_idx += 1

            # Sanitize snippet and cap length for model efficiency
            raw_snippet = item.get("snippet", "") or ""
            clean_snippet = re.sub(r"\s+", " ", raw_snippet).strip()
            capped_snippet = clean_snippet[:1500]

            sources_dict[source_id] = {
                "id": source_id,
                "title": item.get("title", "Untitled").strip(),
                "url": url,
                "domain": extract_domain(url),
                "snippet": capped_snippet,
                "published_date": item.get("published_date")
            }

    return sources_dict
