<!--
═══════════════════════════════════════════════════════════════
SYNC IMPACT REPORT — Constitution Creation
═══════════════════════════════════════════════════════════════

Version Change: N/A → 1.0.0
Date: 2026-03-01
Rationale: Initial constitution ratification for TranslateGemma project

Principles Added:
  I.   Localization-First (NON-NEGOTIABLE)
  II.  API Contract Integrity
  III. Simplicity & YAGNI (NON-NEGOTIABLE)
  IV.  Test-First Development
  V.   UI Layout Consistency
  VI.  Virtual Environment Hygiene
  VII. Observability & Debuggability

Sections Added:
  - Technology Constraints
  - Development Workflow
  - Governance

Templates Requiring Updates:
  ✅ plan-template.md — Constitution Check section present, no update needed
  ✅ spec-template.md — Generic structure aligns with principles, no update needed
  ✅ tasks-template.md — Test-first workflow supported, no update needed

Follow-up TODOs:
  - None. All placeholders filled with concrete values.

Consistency Validations:
  ✅ AGENTS.md — Localization rule (zh-TW) matches Principle I
  ✅ AGENTS.md — API verification rule matches Principle II
  ✅ AGENTS.md — Simplicity rule matches Principle III
  ✅ AGENTS.md — Virtual environment check matches Principle VI
  ✅ README.md — Technology stack matches Technology Constraints
  ✅ Docs/001_requestment.md — Simplicity principle verified

═══════════════════════════════════════════════════════════════
-->

# TranslateGemma Constitution

## Core Principles

### I. Localization-First (NON-NEGOTIABLE)
All specifications, plans, and user-facing documentation MUST be written in Traditional Chinese (zh-TW). Git commit messages, code comments, and inline documentation MUST use Traditional Chinese. Only the constitution itself is written in English and MUST be accompanied by `constitution_zhTW.md` in the same directory.

**Rationale**: This project serves Traditional Chinese users as a primary audience. Consistent localization ensures accessibility, maintainability, and alignment with the user base. English-only technical artifacts create barriers for the development team and stakeholders.

### II. API Contract Integrity
When the frontend calls a backend API or function, the API/function MUST actually exist on the backend. Frontend developers MUST NOT arbitrarily name, assume, or invent APIs. All API definitions MUST be verified against backend implementation before integration.

**Rationale**: Assumed APIs lead to runtime failures, integration delays, and brittle contracts. Explicit verification enforces discipline and reduces debugging overhead in a microservices architecture (Blazor WASM ↔ FastAPI).

### III. Simplicity & YAGNI (NON-NEGOTIABLE)
Avoid over-design and over-engineering. Features MUST solve immediate, validated problems. Speculative abstractions, premature optimizations, and unnecessary complexity are prohibited unless explicitly justified and approved.

**Rationale**: The project explicitly states "設計原則：簡單為主" (simplicity-first). This is a focused translation service without user accounts or persistence. Feature creep undermines maintainability and deployment speed.

### IV. Test-First Development
All new features and bug fixes MUST include automated tests before implementation. Tests MUST cover:
- Unit tests for business logic (backend model inference, frontend services)
- Integration tests for API contracts (backend routes ↔ frontend services)
- E2E tests for critical user flows (translation submission, streaming response, language selection)

Tests MUST be written, reviewed, approved, and failing before implementation begins. Follow the Red-Green-Refactor cycle.

**Rationale**: The project has established `backend/tests/unit/` and `backend/tests/integration/` directories. Test-first development prevents regressions, documents intent, and enables safe refactoring in a GPU-accelerated ML inference pipeline where debugging is expensive.

### V. UI Layout Consistency
Frontend UI components MUST account for consistent layout height. Input fields, chat bubbles, and their placement MUST maintain visual harmony across the interface. Component height, padding, and spacing MUST follow a unified design system (MudBlazor theme customizations documented in codebase).

**Rationale**: Explicitly stated in development guidelines. Inconsistent UI degrades user experience and creates maintenance debt when scaling component library.

### VI. Virtual Environment Hygiene
Before creating a Python virtual environment (e.g., `.venv`), MUST check if one already exists in the project root. If present, reuse it. Do NOT create duplicate or nested virtual environments.

**Rationale**: Explicitly stated in development guidelines. Duplicate environments cause dependency conflicts, waste disk space, and complicate CI/CD pipelines.

### VII. Observability & Debuggability
All backend API endpoints MUST implement structured logging (JSON format) with request ID tracing. Model inference MUST log:
- Device used (CUDA/MPS/CPU)
- Token counts (input/output)
- Latency metrics (tokenization, inference, post-processing)

Frontend MUST log API call failures with full error context (status code, response body, request payload) to browser console.

**Rationale**: TranslateGemma inference involves GPU acceleration, streaming responses, and multi-language tokenization. Debugging production issues without structured logs is impractical. SSE streaming failures are notoriously hard to diagnose without client-side logging.

## Technology Constraints

### Approved Stack
- **Frontend**: Blazor WebAssembly (.NET 9), MudBlazor UI library
- **Backend**: Python 3.13 (required for PyTorch CUDA wheels), FastAPI, Transformers (Hugging Face)
- **Model**: TranslateGemma 4B / 12B (configurable via `config.yaml`)
- **Containerization**: Podman / Docker with multi-stage builds
- **GPU Support**: NVIDIA CUDA 12.4+, Apple MPS, CPU fallback

Changes to core stack require architecture review and migration plan approval.

### Prohibited Patterns
- No client-side state persistence (localStorage/sessionStorage) beyond current page session
- No user authentication or account management
- No database or persistent storage layer
- No client-side model inference (WASM constraints prohibit TranslateGemma)

## Development Workflow

### Code Review Gates
All pull requests MUST pass:
1. Automated test suite (`pytest backend/tests/` for backend, `dotnet test` for frontend)
2. Linting (Python: `ruff`, C#: built-in analyzer)
3. Constitution compliance check (manual verification by reviewer)
4. At least one approving review from maintainer

### Containerization Standards
All Containerfiles MUST:
- Use multi-stage builds to minimize image size
- Pin base image versions (e.g., `mcr.microsoft.com/dotnet/aspnet:9.0.1`)
- Declare HEALTHCHECK endpoints
- Document GPU passthrough requirements in comments
- Follow guidance in `.github/skills/container-image-hygiene/SKILL.md`

### Configuration Management
Runtime configuration MUST be externalized in `config.yaml`. Hardcoded paths, model names, or device selections are prohibited. The schema MUST be validated on startup and reject invalid configurations loudly (fail-fast).

## Governance

This constitution supersedes all conflicting practices, guidelines, or preferences. Amendments require:
1. Documented justification with architectural impact analysis
2. Approval from project maintainers
3. Migration plan for affected code/docs (if breaking change)

All PRs and code reviews MUST verify compliance with this constitution. Complexity MUST be justified against Principle III (Simplicity & YAGNI).

For runtime development guidance and operational procedures, refer to `AGENTS.md` and `.github/copilot-instructions.md`.

**Version**: 1.0.0 | **Ratified**: 2026-03-01 | **Last Amended**: 2026-03-01
