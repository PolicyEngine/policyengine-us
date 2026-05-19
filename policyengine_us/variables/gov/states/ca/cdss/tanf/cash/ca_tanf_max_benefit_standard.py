from policyengine_us.model_api import *


class ca_tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2024/24-55.pdf#page=7",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.CA
    documentation = """
    Returns the Region 1 non-exempt Maximum Aid Payment, matching the CBPP
    and Welfare Rules Database convention for cross-state comparison.
    Region 1 covers California's higher cost-of-living counties (including
    Los Angeles, the most populous county) and is the figure CBPP and Urban
    WRD publish as the California benchmark.

    For actual household-specific calculations, use ca_tanf_maximum_payment,
    which routes by the household's county and exemption status.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.cash.monthly_payment
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_au_size)
        return p.region1.non_exempt[capped_size]
