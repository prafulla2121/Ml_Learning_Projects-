from typing import List, Dict, Any, Optional

class GLRulesEngine:
    """
    Evaluates GL mapping rules for a client.
    Rules format example:
    [
        {"field": "vendor", "operator": "equals", "value": "Amazon", "target_gl": "6200"},
        {"field": "amount", "operator": "greater_than", "value": 5000, "action": "require_approval"}
    ]
    """
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules

    def evaluate(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        results = {
            "target_gl": None,
            "require_approval": False,
            "applied_rules": []
        }

        for rule in self.rules:
            if self._matches(rule, transaction):
                results["applied_rules"].append(rule)
                if "target_gl" in rule:
                    results["target_gl"] = rule["target_gl"]
                if rule.get("action") == "require_approval":
                    results["require_approval"] = True
                if rule.get("action") == "always_flag":
                    results["require_approval"] = True

        return results

    def _matches(self, rule: Dict[str, Any], transaction: Dict[str, Any]) -> bool:
        field = rule.get("field")
        operator = rule.get("operator")
        rule_value = rule.get("value")

        trans_value = transaction.get(field)
        if trans_value is None:
            return False

        if operator == "equals":
            return str(trans_value).lower() == str(rule_value).lower()
        elif operator == "contains":
            return str(rule_value).lower() in str(trans_value).lower()
        elif operator == "greater_than":
            try:
                return float(trans_value) > float(rule_value)
            except (ValueError, TypeError):
                return False
        elif operator == "less_than":
            try:
                return float(trans_value) < float(rule_value)
            except (ValueError, TypeError):
                return False

        return False
