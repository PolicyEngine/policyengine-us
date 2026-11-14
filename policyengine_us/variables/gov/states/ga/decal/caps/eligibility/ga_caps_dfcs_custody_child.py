from policyengine_us.model_api import *


class ga_caps_dfcs_custody_child(Variable):
    value_type = bool
    entity = Person
    label = "Child in DFCS custody, served by Georgia CAPS as a family unit of one"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=27",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=2",
    )

    def formula(person, period, parameters):
        # CAPS/00-5, 5.4.1: the State stands as the parent of each child in DFCS
        # custody, and the child forms a family unit of one. CAPS/00-7, 7.5: foster
        # parents need not meet the income or activity requirements, and the child
        # owes no family fee.
        eligible_child = person("ga_caps_eligible_child", period)
        return eligible_child & person("is_in_foster_care", period)
