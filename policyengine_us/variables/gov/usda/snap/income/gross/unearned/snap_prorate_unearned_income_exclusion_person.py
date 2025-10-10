from policyengine_us.model_api import *


class snap_prorate_unearned_income_exclusion_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "SNAP prorated unearned income exclusion per person"
    documentation = "Amount of unearned income excluded per person due to SNAP proration rules for ineligible household members"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_1"
    unit = USD
    defined_for = "is_snap_ineligible_member_based_on_immigration_status"

    def formula(person, period, parameters):
        unearned_income = person("snap_unearned_income_person", period)
        prorate_fraction = person.spm_unit(
            "snap_ineligible_members_fraction", period.this_year
        )
        return unearned_income * prorate_fraction
