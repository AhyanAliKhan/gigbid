"""
GigBid Explicit Memory Promotion Rules
Analyzes diffs between agent proposal drafts and human edits.
Promotes persistent style memory ONLY when consistent patterns recur across at least two user edits.
Promotes outcome memory ONLY from confirmed client replies or hires.
"""

import difflib
from typing import Dict, Any, Optional
from agent.memory.store import memory_store

# In-memory buffer tracking candidate pattern observations before promotion
OBSERVED_EDIT_PATTERNS: Dict[str, Dict[str, int]] = {}

def analyze_draft_diff(original_text: str, edited_text: str) -> Dict[str, Any]:
    """Analyzes differences between the generated draft and the user's approved edit."""
    orig_lines = original_text.splitlines()
    edited_lines = edited_text.splitlines()
    
    diff = list(difflib.unified_diff(orig_lines, edited_lines, lineterm=""))
    
    deleted_text = " ".join([l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]).lower()
    added_text = " ".join([l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]).lower()

    patterns_detected = []

    # Check 1: Introductory greeting cut
    if any(cliche in deleted_text for cliche in ["dear", "i am excited", "passionate", "i hope this finds you well"]):
        patterns_detected.append("cut_generic_intro")

    # Check 2: Word count reduction
    orig_words = len(original_text.split())
    edit_words = len(edited_text.split())
    if edit_words < orig_words * 0.75:
        patterns_detected.append("concise_shortening")

    # Check 3: Addition of explicit metric or test suite mention
    if any(term in added_text for term in ["test suite", "ci/cd", "coverage", "benchmark", "p95"]):
        patterns_detected.append("emphasize_benchmarks")

    return {
        "word_diff": edit_words - orig_words,
        "patterns_detected": patterns_detected,
        "diff_summary": "\n".join(diff[:8])
    }

def process_user_edit_for_promotion(
    user_id: str,
    original_text: str,
    edited_text: str
) -> Optional[Dict[str, Any]]:
    """Evaluates user edit diff and promotes to Long-Term Memory if threshold is met."""
    analysis = analyze_draft_diff(original_text, edited_text)
    user_patterns = OBSERVED_EDIT_PATTERNS.setdefault(user_id, {})
    
    promoted_rule = None

    for pattern in analysis["patterns_detected"]:
        user_patterns[pattern] = user_patterns.get(pattern, 0) + 1
        # Explicit promotion rule: promote after 2 consistent observations
        if user_patterns[pattern] >= 2:
            if pattern == "cut_generic_intro":
                rule_desc = "Always omit formal greetings and promotional pleasantries; begin immediately with technical deliverables."
            elif pattern == "concise_shortening":
                rule_desc = "Keep proposals strictly under 200 words, focusing purely on architectural proof points."
            elif pattern == "emphasize_benchmarks":
                rule_desc = "Always cite specific benchmarking metrics or automated test coverage in the technical approach."
            else:
                rule_desc = f"Maintain user style preference: {pattern}"

            promoted_rule = memory_store.add_style_rule(
                user_id=user_id,
                rule=rule_desc,
                evidence=f"Observed {user_patterns[pattern]} consistent edits removing or modifying this pattern."
            )
            # Reset counter after promotion
            user_patterns[pattern] = 0

    return promoted_rule

def process_outcome_for_promotion(
    category: str,
    proposal_text: str,
    outcome: str,
    sample_size: int = 15
) -> Optional[Dict[str, Any]]:
    """Promotes winning strategy patterns to Outcome Memory."""
    if outcome.lower() not in ["won", "replied", "interview"]:
        return None

    if "low-latency" in proposal_text.lower() or "benchmark" in proposal_text.lower():
        pattern = "Proposals highlighting concrete latency benchmarks achieve superior reply rates in this category."
    elif "test" in proposal_text.lower() or "playwright" in proposal_text.lower():
        pattern = "Proposals citing comprehensive end-to-end test suites show highest conversion."
    else:
        pattern = "Direct deliverable mapping with verified case studies converts best."

    return memory_store.promote_outcome_memory(
        category=category,
        pattern=pattern,
        sample_size=sample_size
    )
