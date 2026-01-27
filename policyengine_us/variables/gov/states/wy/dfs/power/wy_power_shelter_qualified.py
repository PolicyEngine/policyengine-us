from policyengine_us.model_api import *


class wy_power_shelter_qualified(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming POWER shelter qualified"
    definition_period = MONTH
    reference = "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/"
    defined_for = StateCode.WY
    default_value = True
    # Shelter qualified (Code N) applies when the unit is responsible for
    # paying all or a portion of shelter costs.
    #
    # Set to False (shelter disqualified) when:
    # - Code Y: No obligation to pay shelter costs (completely furnished)
    # - Code R: Unit lives in government housing subsidy
    # - Code M: Minor parent with dependent children living with parent(s),
    #           adult relative, or court-appointed guardian/custodian
    # - Code S: Unit excludes an individual due to receiving SSI
    #
    # Per ARW Chapter 1, Section 9.
