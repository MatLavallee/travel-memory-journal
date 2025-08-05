## Technology Stack Preferences

### Core Development Stack
- **Dependency Management**: uv + pyproject.toml
- **CLI Framework**: Typer
- **Validation & Models**: Pydantic
- **Testing**: pytest + pytest-mock + coverage[toml] + httpx

### Code Quality & Development Tools
- **Linting**: ruff + mypy + sqlfluff
- **Task Runner**: Poe the Poet
  - `poe install` - install dependencies
  - `poe typecheck` - mypy type checking
  - `poe lint` - both SQL and Python linting
  - `poe fix` - auto-fix both SQL and Python
  - `poe dev` - watch mode with lint/test/launch services
  - `poe test` - pytest + coverage
  - `poe ui` - launch UI + API

### Data & Analytics
- **Simple Data Processing**: 
  - Pydantic models
  - Function pipeline pattern (ELT)

### Databases & Storage
- **Database**: local json files

A production-grade AI system typically flows like this:

    1. Ingest raw data → validate → store in lakehouse/vector DB.
    2. Generate features & embeddings → register in store.
    3. Train or fine-tune models; record experiments, metrics, lineage.
    4. Register trained model; pass governance checks.
    5. Deploy behind scalable inference gateway or in-app edge runtime.
    6. Serve via RAG pipeline; prompts pulled from your prompt registry.
    7. Observe logs, metrics, user feedback; trigger automated retraining.
    8. Enforce safety filters and compliance throughout.

way too complicated, but the overall pipeline can potentially be replicated by only using local components. 
