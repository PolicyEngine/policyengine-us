from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ak.dpa.hap.ak_hap_base_benefit import (
    ak_hap_award,
)


class ak_hap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alaska Heating Assistance Program federal LIHEAP component benefit"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3002/3002-1_households.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm",
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
        "https://www.law.cornell.edu/cfr/text/24/965.502",
        "https://www.law.cornell.edu/cfr/text/24/982.517",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap.benefit
        # SPM units approximate separate economic households. This does not
        # distinguish the manual's owner/occupant and room-renter exceptions.
        # Project one first-member marker per SPM unit, regardless of its size.
        first_member = spm_unit.members_position == 0
        household_count = spm_unit.household.sum(first_member)
        sole_household_eligible = spm_unit("ak_hap_base_benefit", period) > 0
        eligible_household_count = spm_unit.household.sum(
            first_member & spm_unit.project(sole_household_eligible)
        )
        heating_expense = spm_unit("heating_expense", period).astype(np.float64)
        dwelling_heating_expense = spm_unit.household.sum(
            first_member * spm_unit.project(heating_expense)
        )
        # 7 AAC 44.080(h) reduces a sharing household's points to its
        # proportionate share of the dwelling's home heating expenses, which
        # 7 AAC 44.900(11) defines to include heat paid indirectly through
        # rent. The heat portion of rent is not observed, so the equal split
        # of manual 3002-1 A.5 fills that gap: each eligible heat-in-rent
        # household gets an equal share among the dwelling's eligible
        # households, at most the maximum share. Households reporting heating
        # bills split the remaining share in proportion to their bills. When
        # no household reports a bill, every household gets the equal share.
        equal_share = where(
            household_count > 1,
            min_(
                1 / max_(eligible_household_count, 1),
                p.maximum_shared_household_share,
            ),
            1,
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period) & (
            heating_expense == 0
        )
        eligible_heat_in_rent_count = spm_unit.household.sum(
            first_member & spm_unit.project(sole_household_eligible & heat_in_rent)
        )
        bill_payer_share = 1 - equal_share * eligible_heat_in_rent_count
        expense_share = np.divide(
            heating_expense * bill_payer_share,
            dwelling_heating_expense,
            out=np.zeros_like(heating_expense),
            where=dwelling_heating_expense > 0,
        )
        share = where(
            (dwelling_heating_expense > 0) & ~heat_in_rent,
            expense_share,
            equal_share,
        )
        return ak_hap_award(spm_unit, period, parameters, share, True)
