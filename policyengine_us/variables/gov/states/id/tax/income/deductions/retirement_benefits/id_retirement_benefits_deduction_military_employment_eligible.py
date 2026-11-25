from policyengine_us.model_api import *
from policyengine_us.tools.filing_requirement import (
    section_6012_gross_income_thresholds,
)


class id_retirement_benefits_deduction_military_employment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Employment income requires a federal return, for the Idaho military retirement benefits deduction"
    documentation = """
    Idaho Code 63-3022A(1)(b)(iii) admits the military retirement benefits of
    a recipient who "Was employed during the tax year and received sufficient
    income from such employment to be required to file a federal return under
    section 6012(a)(1) of the Internal Revenue Code". This is true when the
    person's income from employment, by itself, meets the gross income test
    of the federal filing requirement for the person's return: the gross
    income thresholds of tax_unit_is_required_to_file, without its tests
    for a filer someone can claim as a dependent and for a spouse who loses
    the joint-return exception. Income from employment is gross income as
    section 6012 measures it: wages (Form 1040 line 1a), taxable employer
    dependent care benefits (Form 2441 line 26 and Form 1040 line 1e: the
    benefits section 129(a) and (b) don't exclude, with the exclusion
    limited by the line 16 qualified expenses), gross income from a
    business or farm (Schedule C line 7 and Schedule F line 9, which Chart
    A of the Form 1040 instructions names), and foreign earned income and
    housing amounts the
    person excludes under section 911 (Form 2555 line 43, not the line 50
    housing deduction), which section 6012(c) adds back. As in the federal
    gross income, a loss from one source doesn't reduce income from another.

    The statute and the Form 39R line 8e instructions, which repeat its words
    without the section number, leave four points open. PolicyEngine takes
    these readings:

    1. The test for 2025. For 2018 to 2025, section 6012(f) says "subsection
       (a)(1) shall not apply" and requires a return when gross income
       exceeds the standard deduction, which includes the additions for age
       and blindness. The model applies section 6012(f) for 2025, the federal
       requirement in force that year, and section 6012(a)(1)(A) and (B) from
       2026: at least the basic standard deduction plus the additions for
       age. Applying the (a)(1) thresholds to 2025 would also admit income
       equal to the threshold and leave out blindness, as Chart A of the 2025
       Form 1040 instructions and Publication 501 do: both require a return
       at gross income of "at least" an amount that rises for age alone. The
       model follows section 6012(f), the statute, as
       tax_unit_is_required_to_file does. A literal reading would admit
       nobody for 2025, when (a)(1) requires no return.
    2. Self-employment. Gross income from a business or farm counts as
       income from employment, as wages do.
    3. Joint returns. The person's own income from employment is compared
       with the joint return's threshold, whatever the spouse earns. Section
       6012 itself combines the spouses' gross income.
    4. Self-employment tax returns. Section 6017 requires a return from an
       individual with $400 of net earnings from self-employment. The statute
       names section 6012(a)(1), so that requirement doesn't count here:
       gross income from a business must meet the section 6012 threshold.
    """
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45",
        "https://www.law.cornell.edu/uscode/text/26/6012",
        # Chart A: gross income from a business is Schedule C line 7 or
        # Schedule F line 9.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.retirement_benefits.military.employment
        employment_income = 0
        for source in p.income_sources:
            employment_income = employment_income + max_(
                0, add(person, period, [source])
            )
        employed = employment_income > 0

        # Federal gross income thresholds for the person's tax unit.
        standard_deduction_threshold, basic_threshold = (
            section_6012_gross_income_thresholds(person.tax_unit, period, parameters)
        )
        p_irs = parameters(period).gov.irs
        if p_irs.income.filing_requirement.standard_deduction_rule.applies:
            # Section 6012(f): gross income over the standard deduction, and
            # any gross income on a separate return.
            requires_return = employment_income > standard_deduction_threshold
        else:
            # Section 6012(a)(1)(A) and (B): gross income of at least the
            # basic standard deduction plus the additions for age. A separate
            # return, or one whose standard deduction is zero under section
            # 63(c)(6), has no exception.
            requires_return = employment_income >= basic_threshold
        return p.in_effect & employed & requires_return
