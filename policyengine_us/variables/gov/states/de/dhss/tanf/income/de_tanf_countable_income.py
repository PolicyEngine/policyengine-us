from policyengine_us.model_api import *


class de_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/detanfstateplan2017.pdf#page=6",
    )
    defined_for = StateCode.DE

    # For recipient eligibility and benefit calculation:
    # Countable earned ($90 + $30 + 1/3 + childcare) + countable unearned
    adds = [
        "de_tanf_countable_earned_income",
        "de_tanf_countable_unearned_income",
    ]
