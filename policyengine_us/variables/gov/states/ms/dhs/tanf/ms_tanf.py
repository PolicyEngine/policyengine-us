from policyengine_us.model_api import *


class ms_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "ms_tanf_eligible"
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
        "https://www.mdhs.ms.gov/wp-content/uploads/2019/07/TANF-Manual-Revised_7.19.pdf#page=459",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.tanf
        maximum_benefit = spm_unit("ms_tanf_maximum_benefit", period)
        countable_income = spm_unit("ms_tanf_countable_income", period)
        benefit = max_(maximum_benefit - countable_income, 0)
        benefit = min_(benefit, maximum_benefit)
        # MDHS TANF Policy Manual, Volume III, page 6015: no benefit is
        # issued when the monthly benefit is less than $10.
        return where(benefit >= p.minimum_payment, benefit, 0)
