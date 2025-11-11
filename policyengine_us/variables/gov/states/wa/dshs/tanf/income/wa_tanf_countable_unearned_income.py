from policyengine_us.model_api import *


class wa_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0162",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0025",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get gross unearned income
        # No disregards apply to unearned income for TANF
        gross_unearned = spm_unit("wa_tanf_gross_unearned_income", period)

        return gross_unearned
