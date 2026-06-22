from policyengine_us.model_api import *


class nd_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP family co-payment"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.copay
        # Income is floored at zero so a self-employment loss cannot produce a
        # negative co-payment.
        countable_income = max_(spm_unit("nd_ccap_countable_income", period), 0)
        # hhs_smi is an annual dollar amount; the bare monthly period
        # auto-divides it to a monthly value.
        monthly_smi = spm_unit("hhs_smi", period)
        income_to_smi = where(monthly_smi > 0, countable_income / monthly_smi, 0)
        copay_rate = p.rate.calc(income_to_smi)
        copay = min_(countable_income * copay_rate, countable_income * p.max_rate)
        # The co-payment is waived for families at or below 30% of the state
        # median income and for TANF recipients (400-28-90-20). Diversion and
        # Crossroads recipients are also waived but are not tracked at the
        # moment.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        waived = (income_to_smi <= p.waiver_smi_threshold) | is_tanf_enrolled
        return where(waived, 0, copay)
