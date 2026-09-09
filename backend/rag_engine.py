# rag_engine.py
# ─────────────────────────────────────────────────────────────────
# RAG = Retrieval-Augmented Generation
#
# HOW RAG WORKS:
#   Traditional LLM: User question → LLM generates answer from training data
#                    Problem: LLM may hallucinate or lack domain-specific info
#
#   RAG:             User question
#                         ↓
#                    RETRIEVAL — search knowledge base for relevant docs
#                         ↓
#                    AUGMENT — add retrieved docs to LLM prompt as context
#                         ↓
#                    GENERATION — LLM answers using grounded context
#                    Result: Accurate, source-backed answers
#
# THIS MODULE: Implements the RETRIEVAL step using TF-IDF similarity.
# In production, this would use vector embeddings (OpenAI/Cohere/FAISS).
# ─────────────────────────────────────────────────────────────────
from __future__ import annotations
import re
import math
from typing import List, Dict, Tuple
from knowledge_base import get_all_documents


# ── CONSTANTS ──────────────────────────────────────────────────────
STOP_WORDS = {
    "a","an","the","is","it","in","on","at","to","for","of","and","or",
    "but","do","i","my","me","can","how","what","when","where","why",
    "which","who","will","be","has","have","had","this","that","with",
    "are","was","does","did","not","if","from","by","as","so","your",
    "you","we","they","their","them","our","its","he","she","his","her"
}


# ── TOKENIZER ──────────────────────────────────────────────────────
def tokenize(text: str) -> List[str]:
    """
    Convert raw text into a list of meaningful lowercase tokens.
    Removes stop words and very short tokens.
    
    Example:
        "How do I deposit money?" → ["deposit", "money"]
    """
    words = re.findall(r'[a-z]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


# ── TF-IDF SIMILARITY ──────────────────────────────────────────────
def term_frequency(term: str, doc_tokens: List[str]) -> float:
    """
    TF = count of term in document / total tokens in document
    Measures how frequently a term appears in a document.
    Higher TF = term is more important in this specific document.
    """
    if not doc_tokens:
        return 0.0
    return doc_tokens.count(term) / len(doc_tokens)


def inverse_document_frequency(term: str, all_docs_tokens: List[List[str]]) -> float:
    """
    IDF = log(total documents / documents containing term)
    Rare terms across the corpus get higher IDF scores.
    Common terms (appear in many docs) get lower scores.
    
    Example: "account" appears in all docs → low IDF (not discriminative)
             "RTGS" appears in 1 doc → high IDF (very specific/important)
    """
    n_docs = len(all_docs_tokens)
    n_containing = sum(1 for tokens in all_docs_tokens if term in tokens)
    if n_containing == 0:
        return 0.0
    return math.log(n_docs / n_containing)


def tfidf_score(query_tokens: List[str], doc_tokens: List[str],
                all_docs_tokens: List[List[str]]) -> float:
    """
    Full TF-IDF score between a query and a document.
    Score = sum of TF(term, doc) × IDF(term, corpus) for each query term.
    
    Higher score = document is more relevant to the query.
    """
    score = 0.0
    for term in query_tokens:
        tf  = term_frequency(term, doc_tokens)
        idf = inverse_document_frequency(term, all_docs_tokens)
        score += tf * idf
    return score


# ── COSINE SIMILARITY (bonus scoring) ─────────────────────────────
def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Jaccard similarity = |intersection| / |union|
    Used as a secondary relevance signal alongside TF-IDF.
    """
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


# ── MAIN RAG RETRIEVER ─────────────────────────────────────────────
class RAGEngine:
    """
    The RAG Retrieval Engine.
    
    Loads all knowledge base documents at startup, tokenizes them,
    and provides a retrieve() method that returns the top-k most
    relevant documents for any query.
    
    Architecture:
        Documents → Tokenize → Store token lists
        Query → Tokenize → TF-IDF score vs all docs → Top-K results
    """

    def __init__(self):
        self.documents = get_all_documents()
        # Pre-tokenize all documents for efficiency
        self.doc_tokens: List[List[str]] = []
        self.doc_tag_tokens: List[List[str]] = []
        for doc in self.documents:
            combined_text = doc["title"] + " " + doc["content"]
            self.doc_tokens.append(tokenize(combined_text))
            self.doc_tag_tokens.append(doc.get("tags", []))
        print(f"[RAG] Loaded {len(self.documents)} knowledge base documents")

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.001) -> List[Dict]:
        """
        RETRIEVAL STEP: Find top-k most relevant documents for the query.
        
        Algorithm:
        1. Tokenize the query
        2. Score each document using TF-IDF
        3. Add bonus for tag matches
        4. Sort by score descending
        5. Return top-k results above min_score threshold
        
        Returns:
            List of dicts with keys: id, category, title, content, score
        """
        query_tokens = tokenize(query)
        query_token_set = set(query_tokens)

        if not query_tokens:
            return []

        scored_docs = []
        for i, doc in enumerate(self.documents):
            # Primary score: TF-IDF
            tfidf = tfidf_score(query_tokens, self.doc_tokens[i], self.doc_tokens)

            # Secondary score: tag overlap (Jaccard)
            tag_set = set(self.doc_tag_tokens[i])
            tag_bonus = jaccard_similarity(query_token_set, tag_set) * 0.5

            # Category exact match bonus
            cat_bonus = 0.3 if doc["category"].lower() in query.lower() else 0.0

            final_score = tfidf + tag_bonus + cat_bonus

            if final_score >= min_score:
                scored_docs.append({
                    "id":       doc["id"],
                    "category": doc["category"],
                    "title":    doc["title"],
                    "content":  doc["content"].strip(),
                    "score":    round(final_score, 6),
                })

        # Sort by score descending, return top-k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

    def retrieve_by_category(self, category: str) -> List[Dict]:
        """Return all documents for a specific category."""
        return [
            {"id": d["id"], "category": d["category"],
             "title": d["title"], "content": d["content"].strip()}
            for d in self.documents if d["category"] == category
        ]

    def get_context_string(self, query: str, top_k: int = 3) -> str:
        """
        Convenience method: retrieve docs and format them as a
        context string ready to be injected into an LLM prompt.
        """
        docs = self.retrieve(query, top_k=top_k)
        if not docs:
            return "No relevant information found in knowledge base."
        parts = []
        for i, doc in enumerate(docs, 1):
            parts.append(
                f"[Source {i}: {doc['title']}]\n{doc['content']}"
            )
        return "\n\n---\n\n".join(parts)


# ── SINGLETON INSTANCE ─────────────────────────────────────────────
# Created once at module load — all modules share this instance
rag = RAGEngine()
