from policyengine_us.model_api import *


class wa_rca(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington Refugee Cash Assistance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0020",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-466-0120",
    )
    defined_for = "wa_rca_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("wa_tanf_payment_standard", period)
        countable_income = max_(spm_unit("wa_tanf_countable_income", period), 0)
        return max_(payment_standard - countable_income, 0)
