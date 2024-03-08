from policyengine_us.model_api import *


class al_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Alabama family assistance (TANF)"
    defined_for = StateCode.AL
    definition_period = YEAR
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf"

    def formula(spm_unit, period, parameters):
        # Families are eligible if they have at least one eligible child
        person = spm_unit.members
        eligible_child = person("al_tanf_eligible_child", period)
        eligible_children = spm_unit.any(eligible_child)
        # The family is also required to pass a financial test
        financial_eligibility = spm_unit(
            "al_tanf_financial_eligibility", period
        )
        return eligible_children & financial_eligibility
