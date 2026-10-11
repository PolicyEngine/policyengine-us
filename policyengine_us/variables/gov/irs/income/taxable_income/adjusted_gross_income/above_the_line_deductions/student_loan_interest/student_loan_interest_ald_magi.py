from policyengine_us.model_api import *


class student_loan_interest_ald_magi(Variable):
    value_type = float
    entity = Person
    label = "Modified adjusted gross income for the student loan interest ALD"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Modified adjusted gross income of 26 U.S.C. 221(b)(2)(C): adjusted "
        "gross income determined without regard to section 221 and sections "
        "85(c), 911, 931 and 933 (and, in earlier years, sections 199 and "
        "222), and after application of sections 86, 135, 137, 219 and 469. "
        "Built from gross income sources rather than adjusted gross income, "
        "which includes this deduction. On a joint return each spouse "
        "carries half of the tax unit's deductions and exclusions."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/221#b_2_C",
        "https://www.irs.gov/pub/irs-prior/p970--2024.pdf#page=36",
    )
    defined_for = "student_loan_interest_ald_eligible"

    def formula(person, period, parameters):
        p_irs = parameters(period).gov.irs
        p = p_irs.ald.student_loan_interest.magi
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross_income_sources = list(p_irs.gross_income.sources)
        if "taxable_unemployment_compensation" in gross_income_sources:
            # MAGI is determined without regard to section 85(c), so all
            # unemployment compensation counts, including any amount 85(c)
            # excluded for 2020. Reading the untaxed amount also avoids a
            # cycle: taxable unemployment compensation depends on AGI, which
            # includes this deduction.
            gross_income_sources.remove("taxable_unemployment_compensation")
            gross_income_sources.append("unemployment_compensation")
        total_gross_income = 0
        for source in gross_income_sources:
            total_gross_income += not_dependent * max_(0, add(person, period, [source]))
        person_ald_vars = [f"{ald}_person" for ald in p.person_alds]
        ald_sum_person = add(person, period, person_ald_vars)
        # Deductions for sections 221, 931 and 933 (and 199 and 222 in
        # earlier years) are listed in excluded_alds and not subtracted.
        other_alds = sorted(
            set(p_irs.ald.deductions) - set(p.person_alds) - set(p.excluded_alds)
        )
        ald_sum_taxunit = tax_unit_non_dep_add(
            person.tax_unit,
            period,
            other_alds,
            include_dependents=p_irs.ald.filer_amounts_recorded_on_dependents,
        )
        # Income inputs are net of the section 911 amounts; add them back in
        # full (Form 2555 lines 45 and 50; Pub. 970 Worksheet 4-1 lines 5-6).
        section_911_excluded_income = person.tax_unit(
            "section_911_excluded_income", period
        )
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        frac = where(joint, 0.5, 1.0)
        taxunit_adjustment_shared = (
            not_dependent * (section_911_excluded_income - ald_sum_taxunit) * frac
        )
        modified_adjusted_gross_income = (
            total_gross_income - ald_sum_person + taxunit_adjustment_shared
        )
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            # split basic income evenly between head and spouse
            basic_income_shared = not_dependent * basic_income * frac
            modified_adjusted_gross_income += basic_income_shared
        return modified_adjusted_gross_income
