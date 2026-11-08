import os
import re
import fitz
import numpy as np
import requests
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

from screenplay_parser import parse_screenplay_structure
from builtin_theory import BUILTIN_THEORY_CORPUS

load_dotenv()

SCREENPLAY_ANALYST_SYSTEM_PROMPT = """You are ScriptRAG, an expert screenplay analyst, screenwriting teacher, and film-story consultant.

STRICT DOCUMENT & RELEVANCE RULES:
1. Your primary and authoritative source of truth is the CURRENTLY UPLOADED AND INDEXED SCREENPLAY.
2. Answer questions ONLY using verifiable evidence supported by the active screenplay.
3. NEVER introduce other movies, other screenplays, similar movie titles, actors, directors, external film plots, or general trivia unless the user explicitly requests an external comparison.
4. NEVER connect the uploaded screenplay to another movie merely because titles, character names, or themes appear similar.
5. If the user mentions a specific movie or screenplay title that does not match the active screenplay, respond:
   "The currently uploaded screenplay is [active screenplay name]. Your question appears to refer to a different screenplay. Please upload that screenplay if you want me to analyze it."
6. If the user sends a simple greeting (e.g. "hi", "hello", "hey", "hi nanna"), respond briefly and naturally:
   "Hello! I'm ready to help you analyze the currently uploaded screenplay."
7. Every factual statement about the story must be supported by the uploaded screenplay. If relevant evidence is unavailable, state:
   "I could not find sufficient evidence for this in the currently uploaded screenplay."
8. When theoretical frameworks (Syd Field, Robert McKee, Blake Snyder, John Truby, Christopher Vogler) are applied:
   - The screenplay remains the sole source of story facts.
   - The frameworks provide analytical principles.
   - Never confuse a theory book's example with an event in this screenplay.
   - Cite the screenplay page numbers and theoretical principles separately.

RESPONSE STRUCTURE FOR ANALYTICAL QUESTIONS:
- Direct Answer.
- Screenplay Evidence (with exact page numbers).
- Screenwriting Theory & Framework Reference (citing the relevant author/principle).
- Comparison and Evaluation.
- What Works well in the story.
- What Needs Improvement.
- Specific Suggested Changes.

For factual questions, answer directly with evidence and page citations without unnecessary fluff."""

class EvidenceRAG:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Collection A: Screenplay Data
        self.screenplay_chunks: List[Dict[str, Any]] = []
        self.screenplay_embeddings = None
        self.screenplay_bm25 = None
        self.screenplay_structure: Optional[Dict[str, Any]] = None
        self.screenplay_pages: List[Dict[str, Any]] = []
        self.screenplay_name: str = ""

        # Collection B: Screenwriting Theory (Pre-loaded with built-in master library)
        self.book_chunks: List[Dict[str, Any]] = []
        self.book_embeddings = None
        self.book_bm25 = None
        self.book_names: List[str] = []
        self.hierarchical_summaries: Dict[str, Any] = {}

        # Automatically load built-in filmmaking theory corpus
        self._load_builtin_theory()

    def _load_builtin_theory(self):
        """Loads and indexes the pre-built reference library from Syd Field, McKee, Snyder, Truby, Vogler."""
        self.book_chunks = []
        for item in BUILTIN_THEORY_CORPUS:
            self.book_chunks.append({
                "content": item["content"],
                "page": item["page"],
                "source": item["source"],
                "doc_type": "theory"
            })
            if item["source"] not in self.book_names:
                self.book_names.append(item["source"])

        all_texts = [c["content"] for c in self.book_chunks]
        self.book_embeddings = self.embedding_model.encode(all_texts, show_progress_bar=False)
        tokenized_corpus = [t.lower().split() for t in all_texts]
        self.book_bm25 = BM25Okapi(tokenized_corpus)

    def process_screenplay(self, file_bytes: bytes, filename: str = "screenplay.pdf") -> Dict[str, Any]:
        self.screenplay_name = filename
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        self.screenplay_pages = []

        is_scanned = True
        for page_idx in range(len(doc)):
            text = doc[page_idx].get_text()
            if text.strip():
                is_scanned = False
                self.screenplay_pages.append({
                    "page": page_idx + 1,
                    "text": text,
                    "source": filename
                })
        doc.close()

        if is_scanned or not self.screenplay_pages:
            raise ValueError(f"'{filename}' appears to be empty or a scanned image PDF without selectable text. Please upload a standard text PDF screenplay.")

        # Full deterministic screenplay parse
        self.screenplay_structure = parse_screenplay_structure(self.screenplay_pages)

        # Chunking
        self.screenplay_chunks = []
        for p in self.screenplay_pages:
            splits = self.text_splitter.split_text(p["text"])
            for split in splits:
                self.screenplay_chunks.append({
                    "content": split,
                    "page": p["page"],
                    "source": filename,
                    "doc_type": "screenplay"
                })

        # Dense + BM25 indexing
        chunk_texts = [c["content"] for c in self.screenplay_chunks]
        self.screenplay_embeddings = self.embedding_model.encode(chunk_texts, show_progress_bar=False)
        tokenized_corpus = [c["content"].lower().split() for c in self.screenplay_chunks]
        self.screenplay_bm25 = BM25Okapi(tokenized_corpus)

        self._build_screenplay_hierarchical_summaries()

        return {
            "total_pages": self.screenplay_structure["total_pages"],
            "total_scenes": self.screenplay_structure["total_scenes"],
            "total_chunks": len(self.screenplay_chunks),
            "total_named_characters": self.screenplay_structure["total_named_speaking"],
            "total_unnamed_roles": self.screenplay_structure["total_unnamed_speaking"]
        }

    def process_custom_book(self, file_bytes: bytes, filename: str) -> int:
        """Optional: In case the user ever wants to append their own custom book."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page_idx in range(len(doc)):
            text = doc[page_idx].get_text()
            if text.strip():
                pages.append({"page": page_idx + 1, "text": text, "source": filename})
        doc.close()

        if not pages:
            return 0

        if filename not in self.book_names:
            self.book_names.append(filename)

        new_chunks = []
        for p in pages:
            splits = self.text_splitter.split_text(p["text"])
            for split in splits:
                new_chunks.append({
                    "content": split,
                    "page": p["page"],
                    "source": filename,
                    "doc_type": "theory"
                })

        self.book_chunks.extend(new_chunks)
        all_texts = [c["content"] for c in self.book_chunks]
        self.book_embeddings = self.embedding_model.encode(all_texts, show_progress_bar=False)
        tokenized = [t.lower().split() for t in all_texts]
        self.book_bm25 = BM25Okapi(tokenized)
        return len(new_chunks)

    def _build_screenplay_hierarchical_summaries(self):
        total_p = len(self.screenplay_pages)
        scenes = self.screenplay_structure["scenes"]

        timeline_items = []
        for sc in scenes[:40]:
            chars = ", ".join(sc["characters_speaking"][:3]) or "None"
            action = " ".join(sc["action_lines"][:2])[:120]
            timeline_items.append(f"Sc {sc['scene_number']} (p.{sc['page']}) {sc['heading']} | Chars: [{chars}] | {action}")

        if len(scenes) > 40:
            mid = len(scenes) // 2
            for sc in scenes[mid - 5: mid + 5]:
                chars = ", ".join(sc["characters_speaking"][:3]) or "None"
                action = " ".join(sc["action_lines"][:2])[:120]
                timeline_items.append(f"Sc {sc['scene_number']} (p.{sc['page']}) {sc['heading']} | Chars: [{chars}] | {action}")
            for sc in scenes[-8:]:
                chars = ", ".join(sc["characters_speaking"][:3]) or "None"
                action = " ".join(sc["action_lines"][:2])[:120]
                timeline_items.append(f"Sc {sc['scene_number']} (p.{sc['page']}) {sc['heading']} | Chars: [{chars}] | {action}")

        self.hierarchical_summaries = {
            "total_pages": total_p,
            "total_scenes": len(scenes),
            "timeline_text": "\n".join(timeline_items),
            "act1_range": f"Pages 1 to {int(total_p * 0.25)}",
            "act2_range": f"Pages {int(total_p * 0.25) + 1} to {int(total_p * 0.75)}",
            "act3_range": f"Pages {int(total_p * 0.75) + 1} to {total_p}"
        }

    def _hybrid_retrieve(self, query: str, collection_type: str = "screenplay", top_k: int = 5) -> List[Dict[str, Any]]:
        chunks = self.screenplay_chunks if collection_type == "screenplay" else self.book_chunks
        embeddings = self.screenplay_embeddings if collection_type == "screenplay" else self.book_embeddings
        bm25 = self.screenplay_bm25 if collection_type == "screenplay" else self.book_bm25

        if not chunks or embeddings is None or bm25 is None:
            return []

        q_dense = self.embedding_model.encode([query], show_progress_bar=False)
        dense_scores = cosine_similarity(q_dense, embeddings)[0]

        q_tokens = query.lower().split()
        bm25_scores = np.array(bm25.get_scores(q_tokens))

        if np.max(dense_scores) > np.min(dense_scores):
            dense_norm = (dense_scores - np.min(dense_scores)) / (np.max(dense_scores) - np.min(dense_scores))
        else:
            dense_norm = dense_scores

        if np.max(bm25_scores) > np.min(bm25_scores):
            bm25_norm = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores))
        else:
            bm25_norm = np.zeros_like(bm25_scores)

        combined_scores = 0.65 * dense_norm + 0.35 * bm25_norm
        top_indices = np.argsort(combined_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "page": chunks[idx]["page"],
                "source": chunks[idx]["source"],
                "content": chunks[idx]["content"],
                "score": round(float(combined_scores[idx]), 3)
            })
        return results

    def _call_gemini(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return None, "GEMINI_API_KEY is not configured in .env."

        # gemini-3.5-flash-lite and gemini-3.5-flash have the lowest latency and highest availability
        models_to_try = [
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-flash-latest"
        ]
        last_error = ""

        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.15, "maxOutputTokens": 2048}
            }
            try:
                res = requests.post(url, json=payload, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return text.strip(), None
                else:
                    err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                    last_error = f"{model}: {err}"
            except Exception as e:
                last_error = f"{model} timeout/connection: {str(e)}"

        return None, last_error

    def answer_query(self, query: str) -> Dict[str, Any]:
        if not self.screenplay_chunks:
            return {
                "answer": "Please upload and process a screenplay PDF first.",
                "screenplay_sources": [],
                "book_sources": []
            }

        q_clean = query.strip()
        q_lower = q_clean.lower().rstrip("!?. ")

        # Rule 3: Greeting detection
        # Match greetings like "hi", "hello", "hey", "hi nanna", "good morning", etc.
        greeting_patterns = [
            r"^h[ie]y*(\s.*)?$",
            r"^hello(\s.*)?$",
            r"^good\s+(morning|afternoon|evening)(\s.*)?$",
            r"^what'?s\s+up(\s.*)?$"
        ]
        if any(re.match(pat, q_lower) for pat in greeting_patterns):
            # Check if it's purely a greeting rather than a substantive question about the script
            # e.g., "hi", "hello", "hey there", "hi nanna"
            words = q_lower.split()
            if len(words) <= 3 and not any(term in q_lower for term in [
                "scene", "character", "act", "plot", "climax", "ending", "who", "what is", "where", "why", "how many"
            ]):
                return {
                    "answer": f"Hello! I'm ready to help you analyze the currently uploaded screenplay (**{self.screenplay_name}**).",
                    "screenplay_sources": [],
                    "book_sources": []
                }

        # Route 1: Character Counting / Exact Inventory (uses full deterministic index)
        is_character_count_q = any(term in q_lower for term in [
            "how many characters", "character count", "distinct characters",
            "list all characters", "who speaks", "speaking characters",
            "unnamed roles", "number of characters"
        ])

        if is_character_count_q and self.screenplay_structure:
            struct = self.screenplay_structure
            named_list = []
            for c in struct["named_speaking_characters"]:
                alias_str = f" (Aliases: {', '.join(c['aliases'])})" if c['aliases'] else ""
                named_list.append(f"- **{c['canonical_name']}**{alias_str}: First speaks on Page {c['first_page']} ({c['dialogue_count']} dialogue lines)")

            unnamed_list = [f"- **{u['canonical_name']}**: Speaks on Page {u['first_page']} ({u['dialogue_count']} lines)" for u in struct["unnamed_speaking_roles"][:25]]

            prompt = f"""{SCREENPLAY_ANALYST_SYSTEM_PROMPT}

Complete deterministic screenplay character registry:
Screenplay: {self.screenplay_name} (Total Pages: {struct['total_pages']})
- Total Distinct Named Speaking Characters: {struct['total_named_speaking']}
- Total Distinct Unnamed Speaking Roles: {struct['total_unnamed_speaking']}
- Total Identifiable Individual Speaking Characters: {struct['total_distinct_speaking']}

Inventory of Named Characters:
{chr(10).join(named_list)}

Inventory of Unnamed Roles:
{chr(10).join(unnamed_list)}

User Question: {query}

Provide a direct answer stating the exact counting criteria and inventory without inventing characters."""

            answer_text, err = self._call_gemini(prompt)
            if not answer_text:
                answer_text = f"""### Character Registry Breakdown for {self.screenplay_name}
- **Distinct Named Speaking Characters:** {struct['total_named_speaking']}
- **Distinct Unnamed Speaking Roles:** {struct['total_unnamed_speaking']}
- **Total Identifiable Individual Speaking Characters:** {struct['total_distinct_speaking']}

**Counting Criteria:**
1. Character cues explicitly assigned dialogue.
2. Alias normalization (e.g., merging variants or short names to canonical person).
3. Distinguishing named individuals from generic unnamed roles (e.g., DRIVER, COP).

**Named Characters:**
{chr(10).join(named_list[:15])}
"""
            return {
                "answer": answer_text,
                "screenplay_sources": [{"page": c["first_page"], "source": self.screenplay_name, "content": f"Character: {c['canonical_name']}", "score": 1.0} for c in struct["named_speaking_characters"][:4]],
                "book_sources": []
            }

        # Route 2: Structural, Analytical & Narrative Questions
        is_structural_q = any(term in q_lower for term in [
            "three-act", "three act", "act one", "act two", "act three", "inciting incident",
            "midpoint", "climax", "turning point", "character arc", "resolution", "conflict",
            "stakes", "unnecessary", "pacing", "save the cat", "truby", "field", "mckee"
        ])

        top_k_screenplay = 8 if is_structural_q else 5
        screenplay_matches = self._hybrid_retrieve(query, collection_type="screenplay", top_k=top_k_screenplay)
        book_matches = self._hybrid_retrieve(query, collection_type="book", top_k=5)

        screenplay_context = "\n\n".join([
            f"[SCREENPLAY: {s['source']}, Page {s['page']}]:\n{s['content']}"
            for s in screenplay_matches
        ])

        book_context = "\n\n".join([
            f"[SCREENWRITING THEORY: {b['source']}, Page {b['page']}]:\n{b['content']}"
            for b in book_matches
        ])

        timeline_context = self.hierarchical_summaries.get("timeline_text", "")

        prompt = f"""{SCREENPLAY_ANALYST_SYSTEM_PROMPT}

==============================
ACTIVE UPLOADED SCREENPLAY IDENTIFIER:
Active Screenplay Filename: {self.screenplay_name}
(Note: Treat this script as the ONLY source of story facts. If the user refers to a different movie or screenplay that is not {self.screenplay_name}, politely notify them that {self.screenplay_name} is currently loaded and decline analyzing external films.)
==============================

SCREENPLAY EVIDENCE ({self.screenplay_name}):
Chronological Scene Timeline Sample:
{timeline_context}

Specific Screenplay Excerpts:
{screenplay_context}

==============================
SCREENWRITING & FILMMAKING THEORY (Built-in Knowledge Hub):
{book_context}

==============================
USER QUESTION:
{query}
==============================

Instructions:
- If the question is a greeting, reply with a short friendly greeting.
- If the question mentions a different movie/script name, state: "The currently uploaded screenplay is {self.screenplay_name}. Your question appears to refer to a different screenplay. Please upload that screenplay if you want me to analyze it."
- If the question asks for factual screenplay info not found in the evidence, state: "I could not find sufficient evidence for this in the currently uploaded screenplay."
- For analytical questions, follow this structure:
  - Direct Answer.
  - Screenplay Evidence (with exact page numbers).
  - Screenwriting Theory & Framework Reference (cite author and principle).
  - Comparison and Evaluation.
  - What Works.
  - What Needs Improvement.
  - Specific Suggested Changes.
- For factual questions, answer directly and concisely with page citations."""

        answer_text, err = self._call_gemini(prompt)

        if not answer_text:
            sp_snippets = [f"- (Screenplay Page {s['page']}) {s['content'][:150]}..." for s in screenplay_matches[:3]]
            bk_snippets = [f"- ({b['source']}) {b['content'][:150]}..." for b in book_matches[:2]]
            answer_text = f"API Error ({err}).\n\nRetrieved Screenplay Excerpts:\n" + "\n".join(sp_snippets)
            if bk_snippets:
                answer_text += "\n\nRelevant Theory:\n" + "\n".join(bk_snippets)

        return {
            "answer": answer_text,
            "screenplay_sources": screenplay_matches,
            "book_sources": book_matches
        }
