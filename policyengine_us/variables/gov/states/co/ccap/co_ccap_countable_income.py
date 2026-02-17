from policyengine_us.model_api import *


class co_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program countable income"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=22"
    unit = USD
    defined_for = StateCode.CO
    # 8 CCR 1403-1 Section 7.105: gross income from all sources.
    adds = [
        # Earned income
        "employment_income",
        "self_employment_income",
        "farm_income",
        # Unearned income
        "social_security",
        "pension_income",
        "retirement_distributions",
        "military_retirement_pay",
        "unemployment_compensation",
        "workers_compensation",
        "child_support_received",
        "alimony_income",
        "interest_income",
        "dividend_income",
        "rental_income",
        "veterans_benefits",
        "disability_benefits",
        "capital_gains",
        "gi_cash_assistance",
    ]
