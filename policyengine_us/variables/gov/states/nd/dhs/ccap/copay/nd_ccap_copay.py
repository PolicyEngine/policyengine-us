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
        # The HHS co-pay worksheet charges a flat amount per SMI band equal to
        # the band's co-pay share of monthly SMI (rate x band floor), so the
        # co-pay depends on the family's SMI band rather than its exact income.
        copay_share = p.rate.calc(income_to_smi)
        copay = copay_share * monthly_smi
        # Defensive federal family-share ceiling (45 CFR 98.45(k)): the co-pay
        # never exceeds max_rate of countable income. This does not bind under
        # the current schedule (the band rate tops out at 6%).
        copay = min_(copay, p.max_rate * countable_income)
        # The co-payment is waived for families at or below 30% of the state
        # median income and for TANF recipients (400-28-90-20). Diversion and
        # Crossroads recipients are also waived but are not tracked at the
        # moment.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        waived = (income_to_smi <= p.waiver_smi_threshold) | is_tanf_enrolled
        return where(waived, 0, copay)
