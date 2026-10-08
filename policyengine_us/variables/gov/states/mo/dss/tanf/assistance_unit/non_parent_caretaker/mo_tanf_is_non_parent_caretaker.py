from policyengine_us.model_api import *


class mo_tanf_is_non_parent_caretaker(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF non-parent caretaker relative or legal guardian"
    documentation = (
        "Whether this person cares for the tax unit's dependent children "
        "without being the biological or adoptive parent of any of them, "
        "for example a grandparent, aunt, uncle, adult sibling or legal "
        "guardian. Missouri calls a related caretaker a non-parent caretaker "
        "relative (NPCR) and applies the same rules to a related or "
        "unrelated legal guardian. Mark both spouses when neither is a "
        "parent of the children. With unknown child parent ids, a spouse left "
        "false is presumed to be a parent and excludes the other. Known "
        "parent_1_id and parent_2_id inputs instead identify the parents. "
        "Leave false for parents. A stepparent "
        "living with the child's parent is not a non-parent caretaker, and "
        "neither is a grandparent whose own minor child (the children's "
        "parent) is one of the dependent children. A non-parent caretaker "
        "cannot be included when a parent of the children lives in the "
        "home, unless that parent is a cash-eligible child; mark such a "
        "parent with mo_tanf_is_parent_of_dependent_child (for example an "
        "adult daughter claimed as the grandparent's dependent)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-300",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-40/",
    )
    defined_for = StateCode.MO
