from policyengine_us.model_api import *


class mo_tanf_is_parent_of_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF parent of a dependent child in the tax unit"
    documentation = (
        "Whether this person is the biological or adoptive parent of one of "
        "the tax unit's dependent children. It matters only when someone in "
        "the tax unit is marked as a non-parent caretaker: a parent in the "
        "home, other than a cash-eligible child, excludes that caretaker. "
        "Defaults to having one's own children in the household "
        "(own_children_in_household), which also counts adult children and "
        "children outside the tax unit; set this input directly when that "
        "count does not match. Heads and spouses not marked as non-parent "
        "caretakers are always treated as parents; this input applies to "
        "other tax-unit members."
    )
    definition_period = YEAR
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-05/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        return person("is_parent", period)
