from policyengine_us.model_api import *


class snap_housing_cost_person(Variable):
    value_type = float
    entity = Person
    label = "SNAP prorated housing cost for each person"
    unit = USD
    documentation = "Housing costs at person level with proration for ineligible members (rent and real estate taxes)"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_6"

    def formula(person, period, parameters):
        # Get person-level housing costs
        total_person_housing = add(
            person, period, ["rent", "real_estate_taxes"]
        )

        # Apply proration only for ineligible members
        ineligible_person = person(
            "is_snap_ineligible_member_based_on_immigration_status",
            period.this_year,
        )
        prorate_fraction = person.spm_unit(
            "snap_ineligible_members_fraction", period.this_year
        )

        # Ineligible members get their housing costs reduced by prorate_fraction
        prorated_exclusion = where(
            ineligible_person, total_person_housing * prorate_fraction, 0
        )

        return total_person_housing - prorated_exclusion
