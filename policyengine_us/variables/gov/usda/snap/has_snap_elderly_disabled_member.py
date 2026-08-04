from policyengine_us.model_api import *


class has_snap_elderly_disabled_member(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Has an elderly or disabled SNAP unit member"
    documentation = (
        "Whether the SNAP unit includes an elderly or disabled member. "
        "7 CFR 271.2 defines an elderly or disabled member as a member of "
        "a household; ineligible and nonhousehold members are excluded "
        "from the household, so they do not confer household-wide elderly "
        "or disabled status."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/271.2",
        "https://www.law.cornell.edu/cfr/text/7/273.1",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        elderly = person("is_usda_elderly", period.this_year)
        disabled = person("is_usda_disabled", period.this_year)
        excluded = person("is_snap_excluded_member", period)
        return spm_unit.any((elderly | disabled) & ~excluded)
