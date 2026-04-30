from policyengine_us.model_api import *


class wa_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0035",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0162",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        p = parameters(period).gov.states.wa.dshs.tanf
        size = spm_unit("spm_unit_size", period.this_year)
        size_capped = min_(size, p.maximum_family_size)
        gross_earned_eligible = gross_earned <= p.income.limit[size_capped]

        countable_income = spm_unit("wa_tanf_countable_income", period)
        payment_standard = spm_unit("wa_tanf_payment_standard", period)
        countable_eligible = countable_income < payment_standard

        return gross_earned_eligible & countable_eligible
