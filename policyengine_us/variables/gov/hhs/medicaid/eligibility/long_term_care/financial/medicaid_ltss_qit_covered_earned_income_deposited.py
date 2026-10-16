from policyengine_us.model_api import *


class medicaid_ltss_qit_covered_earned_income_deposited(Variable):
    value_type = float
    entity = Person
    label = "Earned income deposited from sources covered by the Medicaid LTSS qualified income trust"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Actual monthly deposits of the earned sources identified in the "
        "qualified income trust instrument. This factual source component "
        "is a subset of both medicaid_ltss_qit_covered_earned_income and "
        "medicaid_ltss_earned_income_deposited_to_qit. Reporting it separately "
        "avoids excluding the same deposited income twice when the Texas "
        "opening-month rule excludes the entire covered source. Defaults "
        "to no reported covered-source deposits."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust"
