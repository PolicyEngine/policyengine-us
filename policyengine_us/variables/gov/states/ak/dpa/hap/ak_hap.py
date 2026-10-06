from policyengine_us.model_api import *


class ak_hap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alaska Heating Assistance Program benefit"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3002/3002-1_households.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm",
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap.benefit
        base_benefit = spm_unit("ak_hap_base_benefit", period)
        # SPM units approximate separate economic households. This does not
        # distinguish the manual's owner/occupant and room-renter exceptions.
        # Project one first-member marker per SPM unit, regardless of its size.
        first_member = spm_unit.members_position == 0
        household_count = spm_unit.household.sum(first_member)
        eligible_household_count = spm_unit.household.sum(
            first_member & spm_unit.project(base_benefit > 0)
        )
        # Approved convention: household manual A.3-5 applies equal shares to
        # dollar awards, capped at 50% for any sharer. Conflicting earlier
        # points/actual-cost sharing text is documented in the parameter.
        share = where(
            household_count > 1,
            min_(
                1 / max_(eligible_household_count, 1),
                p.maximum_shared_household_share,
            ),
            1,
        )
        # The supplied household allowance is a proxy, not an Alaska schedule;
        # its zero default cannot establish absence. Housing step-down
        # exceptions are unobserved, as are the base formula's tribal,
        # residency and unresolved geography limitations.
        utility_adjustment = (
            spm_unit("receives_housing_assistance", period)
            & ~spm_unit("heat_expense_included_in_rent", period)
            & (spm_unit.household("hud_utility_allowance", period) > 0)
        )
        # Manual step 8 reduces dollars after the base minimum/rounding/cap;
        # 7 AAC 44.080(l)-(n) instead reduces points before the minimum.
        return (
            base_benefit
            * share
            * where(utility_adjustment, 1 - p.utility_allowance_reduction, 1)
        )
