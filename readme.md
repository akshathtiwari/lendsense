## LendSense – Gemini-Powered Mortgage Assistant

_A reference implementation using LangGraph, persistent memory, and tool-calling_

---

### Table of contents

1. [Overview](#overview)
2. [Project layout](#project-layout)
3. [Installation & quick start](#installation--quick-start)
4. [Sample prompts](#sample-prompts)
5. [What’s happening under the hood](#whats-happening-under-the-hood)
6. [Inspecting memory / checkpoints](#inspecting-memory--checkpoints)
7. [Troubleshooting](#troubleshooting)
8. [Production notes](#production-notes)

---

### Overview

LendSense is an AI agent that helps loan officers and customers by:

- **Answering mortgage questions** with Gemini-Flash 2.0.
- **Calling domain tools** on-demand:

  - `LoanCalculator` – EMI / total payment
  - `EligibilityChecker` – FOIR & LTV rules
  - `DocumentParser` – extract PAN/Aadhaar numbers
  - `TavilySearch` – web fallback

- **Remembering multi-turn context** thanks to LangGraph checkpointing into **SQLite**.
- **Recording an immutable audit trail** in `context_store/mcp.json`.

---

### Project layout

```
lendsense/
├─ agents/
│  └─ lendsense_graph.py     ← LangGraph state-machine
├─ tools/                    ← mortgage utilities
├─ memory/
│  └─ mcp_memory.py          ← JSON audit logger
├─ checkpoints.db            ← persistent LangGraph memory (auto-created)
├─ context_store/mcp.json    ← turn-by-turn audit log
├─ main.py                   ← CLI entry point
└─ requirements.txt
```

---

### Installation & quick start

```bash
git clone <repo> && cd lendsense
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# API keys
export GOOGLE_API_KEY="YOUR_GEMINI_FLASH_KEY"
export TAVILY_API_KEY="YOUR_TAVILY_KEY"

python main.py          # launches CLI
```

You’ll see

```
Lendsense is starting... type 'exit' to quit.
```

---

### Sample prompts

Paste each line at the **`User:`** prompt (same session = same memory).

| #   | Demonstrates                    | Prompt                                                                                                                                       |
| --- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Happy-path eligibility**      | `Hi, my net salary is ₹1,55 000. I’ve uploaded PAN ABCDE1234F and Aadhaar 1234 5678 9012. I need a 35 L loan with 15 L down. Am I eligible?` |
| 2   | **FOIR fail**                   | `I earn 22 000 per month and want a 30 L loan with only 5 L down. Am I eligible?`                                                            |
| 3   | **LTV fail**                    | `Salary 70 k, loan 50 L, down-payment 5 L – will this pass?`                                                                                 |
| 4   | **Memory check** (run after #1) | `Remind me how much down-payment I said earlier.`                                                                                            |
| 5   | **Web search fallback**         | `What is the typical mortgage processing time in India?`                                                                                     |

Expected:

- \#1 triggers all three domain tools and may reply “Eligible / Not eligible”.
- \#4 should recall **15 L** because the same `thread_id` keeps memory.

---

### What’s happening under the hood

| Layer         | Tech                                                  | Notes                                            |
| ------------- | ----------------------------------------------------- | ------------------------------------------------ |
| LLM           | `google_genai:gemini-2.0-flash` via `init_chat_model` | Tool-calling JSON                                |
| Orchestration | **LangGraph**                                         | `chatbot` → (tool calls?) → `ToolNode` loop      |
| Checkpointing | `SqliteSaver("checkpoints.db")`                       | One row per node execution; keyed by `thread_id` |
| Tools         | Python functions (`@tool`) + Tavily                   | LoanCalc · Eligibility · DocParser · Search      |
| Audit         | `mcp_memory.py` → `context_store/mcp.json`            | Plain JSON for compliance                        |

---

### Inspecting memory / checkpoints

#### View last state for a thread (Python)

```python
from agents.lendsense_graph import graph
snap = graph.get_state({"configurable": {"thread_id": "1"}})
for m in snap.values["messages"]:
    print(m.type, ":", m.content)        # HumanMessage / AIMessage
```

#### VS Code GUI

1. Install _“SQLite Viewer”_ extension.
2. Open `checkpoints.db` → table **`checkpoints`** → column **`checkpoint`** → right-click **“View Value”**; JSON tree shows `messages`.

---

### Troubleshooting

| Issue                                      | Fix                                                                               |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| `GOOGLE_API_KEY` not found                 | `export GOOGLE_API_KEY=…`                                                         |
| Tool names ignored                         | Ensure `description=` in each `@tool` is precise.                                 |
| Bot forgets after reboot                   | Same `thread_id`? Same `checkpoints.db` path?                                     |
| `sqlite3.OperationalError … executescript` | Use `conn = sqlite3.connect(...); SqliteSaver(conn)` (pass connection, not path). |
| “object not JSON serialisable”             | Confirm `_serialize` helper in `run_lendsense`.                                   |

---

### Production notes

- **Database** – switch to `PostgresSaver("postgresql://user:pass@host/db")` for multi-instance concurrency.
- **Logging / tracing** – integrate with LangSmith or OpenTelemetry via `graph.stream(..., callbacks=[...])`.
- **Clean-up** – run a cron to delete old checkpoints per `thread_id` or move to cold storage.
- **UI** – wrap `run_lendsense` in FastAPI or Streamlit; pass front-end session ID as `thread_id`.

---

Happy automating!
Questions or PRs welcome.
