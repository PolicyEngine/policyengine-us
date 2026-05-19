from policyengine_us.model_api import *


class ct_tfa_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=53",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.CT
    documentation = """
    Returns the Region A regional payment standard, matching the CBPP and
    Welfare Rules Database convention for cross-state comparison. Region A
    covers Connecticut's highest-cost towns (including Stamford and Greenwich)
    and is the figure CBPP and Urban WRD publish as the Connecticut benchmark.

    For actual household-specific calculations, use ct_tfa_payment_standard,
    which routes to the household's region.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_unit_size)
        return p.regional.region_a.amount[capped_size]
