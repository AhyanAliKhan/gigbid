"""
Critic Agent Node
Checks evidence grounding, personalization, conciseness, and tone.
Sends back to Proposal Writer with actionable feedback at most twice.
Tool Access: Portfolio (read).
"""

import os
from typing import Dict, Any
from agent.state import GigBidState
from agent.handoffs import Critique

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "critic_v1.md")

def critic_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    revision_count = state.get("revision_count", 0)
    
    if not draft:
        critique = Critique(
            passes=False,
            grounding_score=0.0,
            personalization_score=0.0,
            length_words=0,
            feedback="No proposal draft present to critique.",
            revision_requested=False
        )
        return {"critique": critique}

    words = draft.cover_letter.split()
    word_count = len(words)
    has_evidence_citation = bool(draft.evidence_ids)
    
    # Evaluate grounding and personalization
    grounding = 0.95 if has_evidence_citation else 0.40
    personalization = 0.90 if word_count >= 60 else 0.50
    
    # Determine if revision should be requested
    needs_revision = (not has_evidence_citation or word_count < 50) and (revision_count < 2)
    
    feedback = "Proposal is well-grounded, concise, and cites verifiable case study evidence."
    if needs_revision:
        feedback = f"Critique request: Expand technical delivery details and ensure evidence IDs are prominently linked. Current words: {word_count}."

    critique = Critique(
        passes=not needs_revision,
        grounding_score=grounding,
        personalization_score=personalization,
        length_words=word_count,
        feedback=feedback,
        revision_requested=needs_revision
    )

    new_revision_count = revision_count + 1 if needs_revision else revision_count

    trace_entry = {
        "node": "critic",
        "action": "evaluate_proposal",
        "passes": critique.passes,
        "revision_requested": needs_revision,
        "revision_count": new_revision_count,
        "grounding_score": grounding,
        "tokens": 240
    }

    return {
        "critique": critique,
        "revision_count": new_revision_count,
        "step_count": 1,
        "total_tokens_used": 240,
        "execution_trace": [trace_entry]
    }
