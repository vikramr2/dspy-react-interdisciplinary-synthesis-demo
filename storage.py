from dataclasses import dataclass
from pathlib import Path
import json
import networkx as nx
import pandas as pd


@dataclass
class SectionChunk:
    domain: str
    paper_id: str
    title: str
    heading: str
    body: str
    doi: str
    chunk_id: str


@dataclass
class PaperNode:
    domain: str
    paper_id: str
    title: str
    doi: str
    authors: str = ""
    year: str = ""


class NeuroGraphStore:
    def __init__(self):
        self.citation_graphs: dict[str, nx.DiGraph] = {}
        self.section_index: dict[str, SectionChunk] = {}   # chunk_id → chunk
        self.paper_index: dict[str, PaperNode] = {}        # "domain/id" → paper

    @classmethod
    def load(cls, base_path: Path) -> "NeuroGraphStore":
        store = cls()

        for domain in ["aiml", "neuroscience", "neuromorphic"]:
            nodes_csv = base_path / domain / f"{domain}_nodes.csv"
            edges_csv = base_path / domain / f"{domain}_edges.csv"

            # Citation graph + author/year metadata
            csv_meta: dict[str, dict] = {}
            if nodes_csv.exists():
                nodes_df = pd.read_csv(nodes_csv)
                for _, row in nodes_df.iterrows():
                    pid = str(row["id"])
                    year = str(row.get("year", row.get("date", ""))).split("-")[0]
                    csv_meta[pid] = {
                        "authors": str(row.get("authors", "") or ""),
                        "year": year,
                    }
                if edges_csv.exists():
                    edges_df = pd.read_csv(edges_csv)
                    store.citation_graphs[domain] = nx.from_pandas_edgelist(
                        edges_df,
                        source=edges_df.columns[0],
                        target=edges_df.columns[1],
                        create_using=nx.DiGraph(),
                    )

            # Paper sections
            papers_json = base_path / domain / f"{domain}_papers_marker.json"
            if not papers_json.exists():
                continue
            for paper in json.loads(papers_json.read_text()):
                paper_id = Path(paper["pdf_filename"]).stem
                key = f"{domain}/{paper_id}"
                meta = csv_meta.get(paper_id, {})

                store.paper_index[key] = PaperNode(
                    domain=domain,
                    paper_id=paper_id,
                    title=paper.get("title", ""),
                    doi=paper.get("doi", ""),
                    authors=meta.get("authors", ""),
                    year=meta.get("year", ""),
                )

                for section in paper.get("sections", []):
                    body = section.get("body", "")
                    if not body.strip():
                        continue
                    heading = section.get("heading", "")
                    slug = heading.lower().replace(" ", "_")[:40]
                    chunk_id = f"{domain}/{paper_id}/{slug}"
                    store.section_index[chunk_id] = SectionChunk(
                        domain=domain,
                        paper_id=paper_id,
                        title=paper.get("title", ""),
                        heading=heading,
                        body=body,
                        doi=paper.get("doi", ""),
                        chunk_id=chunk_id,
                    )

        return store

    def get_citation_neighbors(self, domain: str, paper_id: str) -> dict:
        G = self.citation_graphs.get(domain, nx.DiGraph())
        if paper_id not in G:
            return {"cited_by": [], "cites": []}
        return {
            "cited_by": list(G.predecessors(paper_id)),
            "cites":    list(G.successors(paper_id)),
        }
