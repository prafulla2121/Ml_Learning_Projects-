import pytest
from account_os.backend.app.engine.rules import GLRulesEngine

def test_gl_rules_engine_equals():
    rules = [{"field": "vendor", "operator": "equals", "value": "Amazon", "target_gl": "6200"}]
    engine = GLRulesEngine(rules)

    transaction = {"vendor": "Amazon", "amount": 100}
    result = engine.evaluate(transaction)

    assert result["target_gl"] == "6200"
    assert len(result["applied_rules"]) == 1

def test_gl_rules_engine_no_match():
    rules = [{"field": "vendor", "operator": "equals", "value": "Amazon", "target_gl": "6200"}]
    engine = GLRulesEngine(rules)

    transaction = {"vendor": "Google", "amount": 100}
    result = engine.evaluate(transaction)

    assert result["target_gl"] is None
    assert len(result["applied_rules"]) == 0

def test_gl_rules_engine_greater_than_approval():
    rules = [{"field": "amount", "operator": "greater_than", "value": 1000, "action": "require_approval"}]
    engine = GLRulesEngine(rules)

    transaction = {"vendor": "Apple", "amount": 1500}
    result = engine.evaluate(transaction)

    assert result["require_approval"] is True
    assert len(result["applied_rules"]) == 1

def test_gl_rules_engine_less_than_no_approval():
    rules = [{"field": "amount", "operator": "greater_than", "value": 1000, "action": "require_approval"}]
    engine = GLRulesEngine(rules)

    transaction = {"vendor": "Apple", "amount": 500}
    result = engine.evaluate(transaction)

    assert result["require_approval"] is False
    assert len(result["applied_rules"]) == 0
