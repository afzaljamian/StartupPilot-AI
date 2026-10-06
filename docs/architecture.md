# StartupPilot AI Architecture

```mermaid
flowchart TD
    A[React + Tailwind Frontend] --> B[FastAPI Backend]
    B --> C[JWT Auth]
    B --> D[Celery Queue]
    D --> E[Redis]
    D --> F[CrewAI Coordinator]
    F --> G[Marketing Agent]
    G --> H[Finance Agent]
    H --> I[Product Agent]
    I --> J[Validator Agent]
    G --> K[Tavily]
    H --> K
    F --> L[Gemini]
    B --> M[MongoDB Atlas]
    E --> N[WebSocket Pub/Sub]
    B --> O[ReportLab PDF]
```

## Dependency contract

- Marketing starts from the original startup idea and optional research context.
- Finance receives the completed Marketing output.
- Product receives Marketing + Finance.
- Validator receives Marketing + Finance + Product.
- Important finance arithmetic is performed by Python, not trusted to the LLM.
- WebSockets expose safe progress events only; private reasoning is never streamed.
