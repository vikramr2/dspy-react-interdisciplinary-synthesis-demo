# DSPy ReAct Interdisciplinary Synthesis Demo

A demonstration for ORNL AI4Science showing how to build a [DSPy](https://github.com/stanfordnlp/dspy) ReAct agent that generates cross-disciplinary research hypotheses grounded in real scientific literature.

## What It Does

The agent synthesizes knowledge across three domains — **Neuroscience**, **Neuromorphic Computing**, and **AI/ML** — to generate testable research hypotheses. Given a research question, it retrieves relevant passages from 3,658 papers (~51,500 sections) and reasons across domain boundaries to produce structured hypotheses with evidence chains.

**Example question:** *How can lateral inhibition be implemented in neuromorphic hardware, and why is it useful?*

The agent searches neuroscience literature for how lateral inhibition works biologically, neuromorphic literature for circuit-level implementation strategies, and AI/ML literature for the computational benefits — then synthesizes these into a concrete, cited hypothesis with open validation questions.

## Key Components

| File | Description |
|------|-------------|
| `hypothesis_generation.ipynb` | Main notebook — indexing, tools, agent, and example runs |
| `storage.py` | Loads paper sections and citation graphs per domain |
| `data/{domain}/` | JSON paper data + CSV citation network (not tracked in git) |

## Architecture

```
Research Question
       │
       ▼
  DSPy ReAct Agent  (max 12 iterations)
       │
       ├── search_papers(query, domain)        TF-IDF + sentence-transformer search
       ├── find_cross_domain_links(concept)    Bridge concepts across all 3 domains
       └── get_cited_by(domain, paper_id)      Citation graph traversal (NetworkX)
       │
       ▼
  Structured Hypothesis
  ├── Testable prediction  (If X + Y → Z because ...)
  ├── Evidence bullets     (with paper citations)
  └── Open questions       (2–3 validation directions)
```

## Dataset

| Domain | Papers | Sections |
|--------|--------|----------|
| Neuroscience | 750 | 12,712 |
| Neuromorphic Computing | 1,745 | 16,619 |
| AI/ML | 1,163 | 22,188 |
| **Total** | **3,658** | **51,519** |

## Setup

```bash
pip install dspy sentence-transformers scikit-learn networkx pandas
```

Configure your LM endpoint in the notebook (tested with `gpt-oss-120b` via vLLM).

## Why DSPy + ReAct?

DSPy lets you define the agent's signature declaratively — specifying inputs, outputs, and output field descriptions — without hand-crafting prompts. The ReAct loop interleaves **reasoning** (what do I need to know?) with **acting** (call a tool) and **observation** (what did I find?), making the evidence-gathering process transparent and inspectable. The full reasoning trajectory is available after each run.
