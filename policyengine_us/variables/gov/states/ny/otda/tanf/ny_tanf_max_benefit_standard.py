from policyengine_us.model_api import *


class ny_tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-352",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.NY
    documentation = """
    Returns the basic monthly allowance + home energy + supplemental home
    energy + the maximum NYC shelter allowance, following CBPP and WRD
    conventions for cross-state comparison. NYC is used because it accounts
    for the majority of New York's TANF caseload and is the figure published
    by CBPP and the Urban Welfare Rules Database.

    For actual household-specific calculations, use ny_tanf_need_standard,
    which caps shelter at the household's actual housing cost.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.tanf.need_standard.shelter
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_table_size)
        max_shelter = p.maximum[capped_size]
        non_shelter = add(
            spm_unit,
            period,
            [
                "ny_tanf_basic_monthly_allowance",
                "ny_tanf_home_energy_allowance",
                "ny_tanf_supplemental_home_energy_allowance",
            ],
        )
        return non_shelter + max_shelter
