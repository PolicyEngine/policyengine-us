from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


class vt_reach_up_special_housing_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up special housing allowance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2230A.pdf",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Reach Up Rule 2244.3: SHA is paid only to households whose
        # actual housing expenses exceed the maximum monthly housing
        # allowance (Rule 2246). Amount = min(housing_expenses -
        # max_housing_allowance, $90). SHA is then added to total needs
        # and reduced by the ratable reduction (Rule 2238 / P-2230A).
        # Uses pre-subsidy rent to avoid circular dependency:
        # tanf -> vt_reach_up -> housing_cost -> rent -> housing_assistance
        # -> hud_annual_income -> tanf
        p = parameters(period).gov.states.vt.dcf.reach_up.allowance

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

        county = spm_unit.household("county", period.this_year)
        in_chittenden = county == County.CHITTENDEN_COUNTY_VT
        housing_max = where(
            in_chittenden, p.housing.chittenden, p.housing.non_chittenden
        )

        excess = max_(housing_cost - housing_max, 0)
        return min_(excess, p.special_housing)
