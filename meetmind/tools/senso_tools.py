import requests
import os
import railtracks as rt

SENSO_API = "https://apiv2.senso.ai/api/v1/org"


def _senso_headers():
    key = os.getenv("sensoAI")
    if not key:
        raise RuntimeError("ERROR: sensoAI env var not set")
    return {"X-API-Key": key, "Content-Type": "application/json"}


@rt.function_node
def ingest_to_senso(title: str, summary: str, text: str):
    """Ingest meeting transcript into Senso for future reference.

    Args:
        title (str): Meeting title (e.g. "Sprint Planning - March 28")
        summary (str): Brief meeting summary
        text (str): Full transcript text
    """
    resp = requests.post(
        f"{SENSO_API}/kb/raw",
        headers=_senso_headers(),
        json={"title": title, "summary": summary, "text": text},
        timeout=30,
    )
    data = resp.json()
    if resp.status_code == 202:
        return {"status": "ingested", "id": data.get("id"), "processing_status": data.get("processing_status")}
    return {"status": "failed", "response": str(data)[:300]}


@rt.function_node
def search_senso(query: str):
    """Search past meeting context via Senso Context OS.

    Args:
        query (str): Natural language query about past meetings
    """
    resp = requests.post(
        f"{SENSO_API}/search",
        headers=_senso_headers(),
        json={"query": query, "max_results": 5},
        timeout=30,
    )
    data = resp.json()
    return data.get("answer", data.get("results", str(data)[:300]))


@rt.function_node
def search_past_meetings(topic: str, persona: str):
    """Search past meeting context relevant to a specific persona and topic.

    Args:
        topic (str): The topic to search for
        persona (str): The persona perspective (engineer/designer/pm)
    """
    resp = requests.post(
        f"{SENSO_API}/search",
        headers=_senso_headers(),
        json={"query": f"{topic} - from perspective of {persona}", "max_results": 5},
        timeout=30,
    )
    data = resp.json()
    return data.get("answer", data.get("results", str(data)[:300]))
