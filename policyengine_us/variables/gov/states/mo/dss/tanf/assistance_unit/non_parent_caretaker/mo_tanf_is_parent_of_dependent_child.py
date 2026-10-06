from policyengine_us.model_api import *


class mo_tanf_is_parent_of_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF parent of a dependent child in the tax unit"
    documentation = (
        "Whether this person is the biological or adoptive parent of one of "
        "the tax unit's dependent children. Such a parent is a member of the "
        "assistance unit even when someone else claims them as a tax "
        "dependent, unless they receive SSI or are a dependent child "
        "themselves (then they are a member as a child). A parent in the "
        "home, other than a cash-eligible child, also excludes a non-parent "
        "caretaker. Defaults to having one's own children in the household "
        "(own_children_in_household) and being 12 to 50 years older than one "
        "of the tax unit's dependent children, as of January of the year. "
        "The age window is an imputation rule, not law. The count also "
        "includes adult children and children outside the tax unit, so set "
        "this input directly when it does not match: false, for example, for "
        "a dependent whose own child in the home is an adult, and true for an "
        "adoptive parent outside the 12-to-50-year window. Setting it for one "
        "person for a year sets it to false for everyone else not given a "
        "value for that year, so set it for every parent it applies to; other "
        "years still use the default. Heads and spouses not marked as "
        "non-parent caretakers are always treated as parents; this input "
        "applies to other tax-unit members."
    )
    definition_period = YEAR
    reference = (
        "https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=98e1ef0c1b543650ba12657ae54bcbd1",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-05/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # own_children_in_household counts own children of any age, so on
        # its own it also marks, for example, the head's elderly mother,
        # whose own child in the home is the head. Also require the person
        # to be 12 to 50 years older than at least one of the tax unit's
        # dependent children: a parent is at least 12 at a child's birth,
        # and births after 50 are rare. This window is an imputation rule,
        # not law: the rule covers adoptive parents of any age, so a genuine
        # adoptive parent outside the window needs this input set to true.
        # Dependent children are all under 19, so their ages span less than
        # the 38-year window, and "some child is 12 to 50 years younger"
        # reduces to the youngest being at least 12 years younger and the
        # oldest at most 50.
        # The flag is annual and reads January's dependent children, so a
        # change in who is a dependent child later in the year (for example
        # a child aging out through monthly_age inputs) does not update it.
        has_own_children = person("is_parent", period)
        age = person("age", period)
        dependent_child = person("mo_tanf_dependent_child", period.first_month)
        youngest = person.tax_unit.min(where(dependent_child, age, np.inf))
        oldest = person.tax_unit.max(where(dependent_child, age, -np.inf))
        return has_own_children & (age - youngest >= 12) & (age - oldest <= 50)
