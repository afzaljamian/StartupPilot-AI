import httpx
from datetime import datetime, timezone
from ..config import settings

class TavilyService:
    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        if not settings.tavily_api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post('https://api.tavily.com/search', json={
                    'api_key': settings.tavily_api_key,
                    'query': query,
                    'search_depth': 'advanced',
                    'max_results': max_results,
                    'include_answer': False,
                })
                r.raise_for_status()
                data = r.json()
                return [{
                    'title': x.get('title',''), 'url': x.get('url',''),
                    'content': x.get('content',''),
                    'retrieved_at': datetime.now(timezone.utc).isoformat()
                } for x in data.get('results', [])]
        except Exception:
            return []
