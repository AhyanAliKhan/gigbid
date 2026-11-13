from agent.handoffs import RiskReport, FitReport, BidDecision, PriceQuote, ProposalDraft

def test_risk_score_is_bounded():
    report = RiskReport(score=0.5, flags=[], explanation="sample")
    assert 0 <= report.score <= 1

def test_fit_score_is_bounded():
    report = FitReport(score=0.8, reasoning="Strong fit")
    assert 0 <= report.score <= 1

def test_bid_decision_serialization():
    decision = BidDecision(action="BID", reason="High fit low risk", fit_score=0.88, risk_score=0.12)
    assert decision.action == "BID"
    assert decision.fit_score == 0.88
    assert decision.risk_score == 0.12
