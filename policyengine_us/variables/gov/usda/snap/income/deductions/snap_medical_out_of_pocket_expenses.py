from policyengine_us.model_api import *


class snap_medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = Person
    label = "SNAP medical out-of-pocket expenses"
    unit = USD
    documentation = "Medical out-of-pocket expenses for elderly/disabled SNAP members with proration"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_5"

    def formula(person, period, parameters):
        # Only count medical expenses for elderly or disabled members
        elderly = person("is_usda_elderly", period)
        disabled = person("is_usda_disabled", period)
        elderly_disabled = elderly | disabled

        # Get medical expenses
        moop = person("medical_out_of_pocket_expenses", period)

        # Apply proration for ineligible members
        is_prorate_person = person(
            "is_snap_ineligible_member_based_on_immigration_status",
            period.this_year,
        )
        prorate_fraction = person.spm_unit(
            "snap_ineligible_members_fraction", period.this_year
        )
        prorate_exclusion = where(
            is_prorate_person, moop * prorate_fraction, 0
        )
        moop_after_proration = moop - prorate_exclusion

        # Only return expenses for elderly/disabled members
        return where(elderly_disabled, moop_after_proration, 0)
