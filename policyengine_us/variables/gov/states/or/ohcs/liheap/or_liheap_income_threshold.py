from policyengine_us.model_api import *


class or_liheap_income_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income threshold for Oregon LIHEAP eligibility"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oregon.public.law/rules/oar_813-200-0020"
        "https://www.oregon.gov/ohcs/energy-weatherization/pages/utility-bill-payment-assistance.aspx"
    )

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        state_median_income = spm_unit("hhs_smi", period)
        p = parameters(period).gov.hhs.liheap
        return state_median_income * p.smi_limit
