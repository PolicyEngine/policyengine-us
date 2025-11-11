from policyengine_us.model_api import *


class wa_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0162",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0025",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Sum all person-level TANF gross unearned income
        person_unearned = spm_unit.members(
            "tanf_gross_unearned_income", period
        )
        return spm_unit.sum(person_unearned)
