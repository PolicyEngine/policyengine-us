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
        # proportionate share of the dwelling's heating expenses. When no
        # household reports a heating expense (heat in rent), manual 3002-1
        # A.5 fills the gap: equal shares among the eligible households, at
        # most the maximum share each. A heat-in-rent household that shares a
        # dwelling with a household reporting a heating bill gets a zero share,
        # because the heating portion of its rent is not observed.
        equal_share = where(
            household_count > 1,
            min_(
                1 / max_(eligible_household_count, 1),
                p.maximum_shared_household_share,
            ),
            1,
        )
        share = np.divide(
            heating_expense,
            dwelling_heating_expense,
            out=equal_share,
            where=dwelling_heating_expense > 0,
        )
        return ak_hap_award(spm_unit, period, parameters, share, True)
