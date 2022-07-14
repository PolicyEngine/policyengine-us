from openfisca_us.model_api import *


class spm_unit_total_ccdf_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SPM unit total CCDF copay"
    unit = USD
    reference = "https://www.ocfs.ny.gov/programs/childcare/stateplan/assets/2022-plan/FFY2022-2024-CCDF-Plan.pdf#page=107"

    def formula(spm_unit, period, parameters):
        # Get family income and federal poverty line
        income = spm_unit("ccdf_income", period)
        fpl = spm_unit("spm_unit_fpg", period)
        # Get county and copay percent parameter by county
        county = spm_unit.household("county_str", period)
        p_copay_percent = np.ones_like(county)
        copays = parameters(period).gov.hhs.ccdf.copay_percent
        valid_county = np.isin(county, np.array(list(copays._children)))
        if valid_county.sum() > 0:
            p_copay_percent[valid_county] = parameters(
                period
            ).gov.hhs.ccdf.copay_percent[county[valid_county]]
        income_exceeding_fpl = max_(income - fpl, 0)
        # There is a minimum family fee of $1 per week
        return max_(income_exceeding_fpl * p_copay_percent, 52)
