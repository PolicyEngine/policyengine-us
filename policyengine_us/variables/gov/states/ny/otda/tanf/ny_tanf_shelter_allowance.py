from policyengine_us.model_api import *


class ny_tanf_shelter_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF shelter allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-352.3"

    def formula(spm_unit, period, parameters):
        # Per 18 NYCRR 352.3(a): shelter allowance equals actual rental
        # obligation up to the local agency maximum schedule.
        # Uses pre-subsidy rent to avoid circular dependency:
        # tanf -> ny_tanf -> housing_cost -> rent -> housing_assistance
        # -> hud_annual_income -> tanf
        p = parameters(period).gov.states.ny.otda.tanf.need_standard.shelter
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_table_size)
        shelter_max = p.maximum[capped_size]

        pre_subsidy_rent = add(spm_unit, period, ["pre_subsidy_rent"])
        other_housing = add(
            spm_unit,
            period,
            [
                "real_estate_taxes",
                "homeowners_association_fees",
                "mortgage_payments",
                "homeowners_insurance",
            ],
        )
        housing_cost = pre_subsidy_rent + other_housing
        return min_(housing_cost, shelter_max)
