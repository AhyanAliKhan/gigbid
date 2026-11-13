"""
Portfolio MCP Server Prompt Templates
Realistic prompt templates freelancers and LLM hosts can pick from.
"""

def prompt_answer_screening_question(question: str, skill_context: str = "") -> str:
    """Prompt template: Answer a screening question from my portfolio."""
    return f"""You are drafting an answer to the client's screening question for a freelance proposal.

Client Screening Question:
"{question}"

Candidate Portfolio Context:
{skill_context}

Instructions:
1. Answer directly and concisely in 2-4 sentences.
2. Ground every claim in specific past projects or verified case study IDs.
3. Quantify results where evidence exists (e.g., latency, accuracy, volume).
4. Do not make unverified claims or provide personal contact info.
"""

def prompt_summarize_proof_points(requirement: str, evidence_text: str = "") -> str:
    """Prompt template: Summarize key proof points for requirement."""
    return f"""Extract and summarize the top verified proof points for the following client requirement.

Client Requirement:
"{requirement}"

Available Portfolio Records:
{evidence_text}

Output 2-3 bullet points highlighting:
- The exact project/case study ID
- The technology stack used
- The measurable metric or outcome achieved
"""
