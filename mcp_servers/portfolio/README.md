# Portfolio MCP Server (`portfolio-mcp-server`)

A production-ready Model Context Protocol (MCP) server providing LLM agents (Claude Desktop, Cursor, Antigravity, LangGraph) with verified, read-only access to a freelancer's real project portfolio, case studies, code repositories, and skills.

## Quick Installation & Launch

### Option 1: Run via `uvx` (No install needed)
```bash
uvx portfolio-mcp-server
```

### Option 2: Run via Docker
```bash
docker run -i --rm -e ACTIVE_PERSONA=alex_chen_aiml ghcr.io/gigbid/portfolio-mcp:latest
```

### Option 3: Configure in Claude Desktop or Cursor (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "portfolio": {
      "command": "python",
      "args": ["-m", "mcp_servers.portfolio.server"],
      "env": {
        "ACTIVE_PERSONA": "alex_chen_aiml"
      }
    }
  }
}
```

## Available Tools

1. `search_evidence(requirement: str, k: int = 5, filters: Optional[dict] = None)`
   - Performs semantic and keyword search across verified case studies, GitHub repositories, and client reviews.
   - Returns evidence records with `evidence_id`, `type`, `skills`, `outcome`, and file source.
2. `get_case_study(id: str)`
   - Retrieves full project architecture markdown and verified delivery metrics.
3. `list_skills()`
   - Enumerates all verified technical proficiencies for the active freelancer profile.

## Resource Templates

- `portfolio://case/{id}` — Load complete project case study text.
- `portfolio://proposal/{id}` — Load historical past proposal text and won/replied status.

## Prompt Templates

- `answer_screening_question` — Grounded Q&A answering client questions using real portfolio evidence.
- `summarize_proof_points` — Bulleted extraction of proof points for a proposal deliverable.
