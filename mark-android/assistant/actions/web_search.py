"""
web_search.py
-------------
Adaptiert von actions/web_search.py. Das Original ließ Gemini "grounded"
suchen und fiel auf DuckDuckGo zurück. Auf Android nutzen wir direkt
DuckDuckGo (duckduckgo_search-Paket), das ist leichtgewichtig und braucht
keinen zweiten API-Key.
"""

from duckduckgo_search import DDGS

TOOL = {
    "name": "web_search",
    "description": (
        "Durchsucht das Web. mode='news' für aktuelle Nachrichten, "
        "'research' für tiefergehende Informationen, 'price'/'compare' für "
        "Preisvergleiche, 'search' für allgemeine Suche."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "mode": {
                "type": "string",
                "enum": ["news", "research", "price", "compare", "search"],
            },
        },
        "required": ["query"],
    },
}


def run(query, mode="search"):
    try:
        with DDGS() as ddgs:
            if mode == "news":
                results = list(ddgs.news(query, max_results=5))
                lines = [f"- {r['title']} ({r['source']}): {r['body'][:150]}" for r in results]
            else:
                results = list(ddgs.text(query, max_results=5))
                lines = [f"- {r['title']}: {r['body'][:150]}" for r in results]
        if not lines:
            return "Keine Ergebnisse gefunden."
        return "\n".join(lines)
    except Exception as exc:
        return f"Websuche fehlgeschlagen: {exc}"
