from policyengine_us.model_api import *


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
        # Per Vermont DCF Reach Up Procedure P-2230A: when computing the
        # household maximum benefit, add up to the special housing allowance
        # (maximum of $90) on top of the basic need standard and housing
        # standard, then multiply by the ratable reduction.
        # The special housing allowance is available to households with a
        # shelter obligation; households with no housing costs do not
        # receive it.
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
        has_shelter_costs = (pre_subsidy_rent + other_housing) > 0
        return where(has_shelter_costs, p.special_housing, 0)
