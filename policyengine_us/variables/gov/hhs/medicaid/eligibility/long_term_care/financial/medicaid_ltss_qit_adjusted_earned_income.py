from policyengine_us.model_api import *


class medicaid_ltss_qit_adjusted_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS earned income remaining outside a qualified income trust"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Each person's own gross earned income less their valid qualified "
        "income trust deposits, before Medicaid LTSS income exclusions."
    )
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
    )

    def formula(person, period, parameters):
        income = max_(person("medicaid_ltss_gross_earned_income", period), 0)
        deposits = max_(
            person("medicaid_ltss_earned_income_deposited_to_qit", period), 0
        )
        return max_(income - deposits, 0)
