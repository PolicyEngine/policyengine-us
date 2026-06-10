from policyengine_us.model_api import *


class la_ccap_daily_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP daily co-payment"
    unit = USD
    reference = "https://www.louisianabelieves.com/docs/default-source/early-childhood/ccap-sliding-fee-scale.pdf"
    defined_for = "la_ccap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap
        waived = spm_unit("la_ccap_copay_waived", period)
        income = max_(spm_unit("la_ccap_countable_income", period), 0)
        monthly_smi = spm_unit("la_ccap_smi", period)
        # The sliding fee scale bands are fixed shares of the state median
        # income; the published dollar band tops equal these shares rounded
        # to whole dollars.
        smi_share = where(monthly_smi > 0, income / monthly_smi, 0)
        return where(waived, 0, p.copay.daily_amount.calc(smi_share))
