from policyengine_us.model_api import *


class ma_ccfa_is_parent(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts CCFA parent of an applying child"
    definition_period = YEAR
    defined_for = StateCode.MA
    documentation = (
        "Approximates CCFA parent status from tax roles and known parent "
        "status. Any nondependent adult tax unit head or spouse is treated "
        "as a parent, so a nonparent caretaker, a grandparent heading a "
        "separate tax unit, or an unmarried partner without a common child "
        "is counted even though EEC excludes their income. Nonparent "
        "caretaker households are not supported."
    )
    reference = "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=22"

    def formula(person, period, parameters):
        # NOTE: the default spouse role can select an adult dependent, and
        # minors are never tax unit heads or spouses, so a minor parent is
        # identified by own children in the household.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        dependent = person("is_tax_unit_dependent", period)
        is_child = person("is_child", period)
        is_parent = person("is_parent", period)
        return (head_or_spouse & ~dependent) | (is_child & is_parent)
