from policyengine_us.model_api import *


class is_child_of_medicaid_caretaker(Variable):
    value_type = bool
    entity = Person
    label = "Child in the care of a Medicaid parent or caretaker relative"
    documentation = (
        "Whether the person is a tax-unit dependent whose filer counts as "
        "their parent or other caretaker relative for Medicaid, before any "
        "age test. The parent and caretaker relative group (42 CFR 435.110) "
        "and the adult group's child coverage requirement (42 CFR "
        "435.119(c)) each apply their own age limit to this relationship."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.4",
        "https://www.law.cornell.edu/cfr/text/42/435.110",
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/NJ/NJ-13-0011-MM1.pdf#page=31",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        state = person.household("state_code_str", period)
        # Tax-unit filer roles proxy the caretaker relationship: 42 CFR
        # 435.4 names claiming the child as a tax dependent as an indicator
        # of primary responsibility for the child's care.
        is_dependent = person("is_tax_unit_dependent", period)
        # In states electing the 42 CFR 435.4 paragraph (3) any-adult
        # option on their state plan S25 page, a foster child makes the
        # adult caring for the child a caretaker, whether or not the adult
        # is a relative. Elsewhere foster children are excluded as a proxy:
        # an unrelated foster parent may claim the child as a tax dependent
        # yet is not a relative by blood, adoption, or marriage. Outside
        # electing states this also excludes kinship foster caregivers,
        # whose blood relationship legally survives the foster placement -
        # a known limitation, since the model cannot distinguish the two
        # placements.
        in_foster_care = add(person, period, ["is_in_foster_care"]) > 0
        elects_any_adult = p.caretaker_relative.any_adult_option[state].astype(bool)
        excluded_foster_child = in_foster_care & ~elects_any_adult
        return is_dependent & ~excluded_foster_child
