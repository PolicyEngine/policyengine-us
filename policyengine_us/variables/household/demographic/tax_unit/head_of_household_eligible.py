from policyengine_us.model_api import *


class head_of_household_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for head of household filing status"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2#b",
        "https://www.law.cornell.edu/uscode/text/26/7703#b",
        # "If an individual is a dependent of a taxpayer ..., such individual
        # shall be treated as having no dependents".
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
        # Publication 501. Considered unmarried, test 5: "You must be able to
        # claim the child as a dependent", with an exception only for a
        # noncustodial parent's claim. Table 4: footnote 3 ("the only reason
        # you can't claim the person as a dependent is that you can be
        # claimed as a dependent") is attached only to the married qualifying
        # child row, in each of the 2021-2025 editions.
        # PDF pages 8, 10
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=8",
    )

    def formula(tax_unit, period, parameters):
        # tax_unit_married is true iff a spouse is present in this tax unit.
        # JOINT filers have the spouse in the same unit (married=true);
        # MFS filers have the spouse in a separate unit (married=false).
        # We use this signal to distinguish the IRC 7703(b) treated-unmarried
        # path (MFS, married=false) from a stray is_separated=true on a
        # JOINT filer (married=true), without reading filing_status and
        # creating a circular dependency through filing_status -> hoh_eligible.
        married = tax_unit("tax_unit_married", period)
        person = tax_unit.members
        # IRC 7703(b) "considered unmarried" applies to the taxpayer (head or
        # spouse), not to dependents. A separated dependent must not trigger
        # the 7703(b) child-only qualifying-person path.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_separated = tax_unit.any(is_head_or_spouse & person("is_separated", period))
        # A taxpayer who can be claimed as a dependent by another taxpayer is
        # treated as having no dependents (IRC 152(b)(1)), so is entitled to
        # no section 151 deduction for anyone. That closes the routes below
        # that require the deduction, but not the qualifying child route.
        # The flag does not depend on filing status, so reading it here
        # creates no cycle through filing_status.
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        # IRC 2(b)(1)(A)(i): a qualifying child as defined in section 152(c),
        # which does not require that the taxpayer can claim the child.
        # Permanently disabled dependents meet its age test under
        # 152(c)(3)(B), as in is_qualifying_relative_dependent.
        is_qualifying_child = person("is_qualifying_child_dependent", period)
        is_disabled_dependent = person(
            "is_permanently_and_totally_disabled", period
        ) & person("is_tax_unit_dependent", period)
        # IRC 2(b)(1)(A)(ii) and (B): any other dependent, including a
        # parent, counts only "if the taxpayer is entitled to a deduction for
        # the taxable year for such person under section 151". Qualifying
        # relatives only count if related per IRC 2(b)(3).
        is_qualifying_relative = person("is_qualifying_relative_dependent", period)
        is_related = person("is_related_to_head_or_spouse", period)
        relative_counts = (
            is_qualifying_relative & is_related & ~tax_unit.project(dependent_elsewhere)
        )
        is_hoh_qualifying = is_qualifying_child | is_disabled_dependent | relative_counts
        has_qualifying_person = tax_unit.sum(is_hoh_qualifying) > 0
        # IRC 7703(b) treated-unmarried status supports HoH only through the
        # child-abode path, not the broader qualifying-relative route.
        # IRC 7703(b)(1) further requires the taxpayer to file a separate
        # return: a JOINT filer who is separated cannot claim HoH because
        # the joint return forecloses the "considered unmarried" path.
        treated_unmarried_qualifies = tax_unit.sum(is_qualifying_child) > 0
        surviving_spouse = tax_unit("surviving_spouse_eligible", period)
        unmarried_qualifies = has_qualifying_person & ~married & ~is_separated
        # ~married masks the JOINT-with-is_separated=true case: a JOINT
        # filer cannot use IRC 7703(b)(1) because they have not filed a
        # separate return. MFS filers (spouse in a different tax unit) have
        # married=false and continue to qualify via this branch.
        # IRC 7703(b)(1) also requires a child "with respect to whom such
        # individual is entitled to a deduction for the taxable year under
        # section 151 (or would be so entitled but for section 152(e))", so a
        # separated taxpayer who can be claimed as a dependent stays married
        # and files separately.
        separated_qualifies = (
            treated_unmarried_qualifies
            & is_separated
            & ~married
            & ~dependent_elsewhere
        )
        return (unmarried_qualifies | separated_qualifies) & ~surviving_spouse
