from policyengine_us.model_api import *


class ma_ccfa_is_parent(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts CCFA parent of an applying child"
    definition_period = YEAR
    defined_for = StateCode.MA
    documentation = (
        "Approximates CCFA parent status from known parent status and tax "
        "roles. Anyone with own children in the household is a parent at "
        "any age; otherwise any nondependent adult tax unit head or spouse "
        "is treated as a parent, so a nonparent caretaker, a grandparent "
        "heading a separate tax unit, or an unmarried partner without a "
        "common child is counted even though EEC excludes their income. "
        "Nonparent caretaker households are not supported."
    )
    reference = "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=22"

    def formula(person, period, parameters):
        # NOTE: tax roles are a fallback: the default spouse role can select
        # an adult dependent, and a minor or dependent parent is never a
        # tax unit head or spouse.
        is_parent = person("is_parent", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        dependent = person("is_tax_unit_dependent", period)
        return is_parent | (head_or_spouse & ~dependent)
