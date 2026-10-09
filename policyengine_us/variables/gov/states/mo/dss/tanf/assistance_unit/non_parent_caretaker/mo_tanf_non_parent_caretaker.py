from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
)


class mo_tanf_non_parent_caretaker(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF non-parent caretaker considered for the assistance unit"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-300",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-05/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-40/",
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-1994-title42-section606&num=0&edition=1994",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # A caretaker is a tax-unit head or spouse, not claimed as a
        # dependent, whose tax unit has a dependent child; see
        # mo_tanf_is_assistance_unit_member.
        dependent_child = person("mo_tanf_dependent_child", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        caretaker = (
            head_or_spouse & ~is_dependent & person.tax_unit.any(dependent_child)
        )
        non_parent = person("mo_tanf_is_non_parent_caretaker", period.this_year)
        # 13 CSR 40-2.300(5)(D) admits a needy non-parent caretaker relative
        # or guardian only "if there are no natural or adoptive parents in
        # the home", and DSS Manual 0210.005.10 excludes "A legal guardian
        # or NPCR if a biological or adoptive parent is in the home." Two
        # signals mark a parent in the home:
        # - a caretaker not marked as a non-parent, presumed to be a parent
        #   only for unknown child parent ids, or identified by the parent
        #   flag, including one who receives SSI (excluded from the unit,
        #   but still in the home);
        # - any other member of the tax unit marked as a parent of a
        #   dependent child, such as an adult daughter claimed as the
        #   grandparent's dependent. A parent who is a cash-eligible child
        #   is left out: DSS Manual 0210.005.05 makes the parent the
        #   caretaker payee "unless that parent is also a cash eligible
        #   child". A minor parent on SSI is not cash-eligible
        #   (0210.005.10), so she still counts.
        # The check covers the tax unit only, so a parent who files a
        # separate return is not seen.
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        cash_eligible_child = dependent_child & ~is_ssi_recipient
        parent = person("mo_tanf_is_parent_of_dependent_child", period.this_year)
        other_parent = parent & ~cash_eligible_child
        unknown_child = dependent_child & ~has_parent_ids(person, period.this_year)
        # A known child's ids override the presumed parenthood of an
        # unmarked head/spouse; retain the proxy only for unknown links.
        parent_caretaker = caretaker & (parent | person.tax_unit.any(unknown_child))
        parent_in_home = person.tax_unit.any(
            (parent_caretaker | other_parent) & ~non_parent
        )
        # DSS Manual 0210.005.35: an NPCR who receives SSI, SSI-SP or SP
        # cannot have their needs and income included. SP receipt is not
        # observable (see mo_tanf_is_assistance_unit_member).
        candidate = caretaker & non_parent & ~parent_in_home & ~is_ssi_recipient
        # One caretaker relative per married couple. This is an
        # interpretation: no Missouri source addresses two spouses who are
        # both relatives of the child. DSS Manual 0210.005.35 budgets "the
        # NPCR" together with "his/her spouse" and treats the spouse as a
        # separate person whose absence or SSI makes the NPCR needy. The
        # AFDC definition Missouri's rules descend from covered "the needs
        # of the relative with whom any dependent child is living (and the
        # spouse of such relative ... if such relative is the child's
        # parent ...)" (42 U.S.C. 606(b), 1994 edition), adding the spouse
        # only for a parent. So the other spouse enters only the neediness
        # budget. Take the tax-unit head, or the spouse when the head
        # cannot be included.
        head = person("is_tax_unit_head", period.this_year)
        head_is_candidate = person.tax_unit.any(candidate & head)
        return candidate & (head | ~head_is_candidate)
