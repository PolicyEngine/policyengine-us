from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nh.dhhs.ssp._nh_ssp_couple import (
    nh_ssp_spouse,
    spouse_value,
)


class nh_ssp_assistance_group_size(Variable):
    value_type = int
    entity = Person
    label = "New Hampshire adult category assistance group size"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"

    def formula(person, period, parameters):
        # He-W 658.03(b): one person, plus a spouse or a needy essential person
        # in an independent living arrangement (2), or both (3).
        arrangement = person("nh_ssp_living_arrangement", period)
        independent = arrangement == arrangement.possible_values.INDEPENDENT
        spouse = nh_ssp_spouse(person, period)
        has_essential_person = person("nh_ssp_has_essential_person", period)
        essential = independent & (
            has_essential_person | spouse_value(has_essential_person, spouse, False)
        )
        return 1 + (spouse >= 0) + essential
