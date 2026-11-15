from policyengine_us.model_api import *


class ok_federal_eitc_demographic_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets demographic eligibility for EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=930",
        # IRC 32(c)(1)(A)(ii), 2020 edition of the United States Code
        "https://www.govinfo.gov/content/pkg/USCODE-2020-title26/html/USCODE-2020-title26-subtitleA-chap1-subchapA-partIV-subpartC-sec32.htm",
        "https://www.irs.gov/pub/irs-prior/p596--2020.pdf#page=16",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/p4012--2021.pdf#page=61",
    )
    defined_for = StateCode.OK
    documentation = """
    Demographic eligibility for EITC using FROZEN 2020 parameters.

    Tax units are demographically eligible if:
    1. They have qualifying children, OR
    2. At least one filer meets age requirements (without children), and
       neither filer can be claimed as a dependent on another return

    2020 Age requirements (for filers without qualifying children):
    - Minimum age: 25 for students and nonstudents
    - Maximum age: 64

    Note: If the tax unit has qualifying children, age requirements
    do not apply to the filers.
    """

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # If tax unit has qualifying children, automatically eligible
        has_child = tax_unit("eitc_child_count", period) > 0
        age = person("age", period)
        # Use FROZEN 2020 age parameters per Oklahoma statute
        min_age_non_student = parameters.gov.irs.credits.eitc.eligibility.age.min(
            "2020-01-01"
        )
        min_age_student = parameters.gov.irs.credits.eitc.eligibility.age.min_student(
            "2020-01-01"
        )
        student = person("is_full_time_student", period)
        # Both frozen 2020 minimum ages equal 25.
        min_age = where(student, min_age_student, min_age_non_student)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max("2020-01-01")
        # Check if at least one filer meets age requirements. The age test
        # applies to the filer or, on a joint return, either spouse, never to
        # a dependent (IRC 32(c)(1)(A)(ii)(II)).
        meets_age_requirements = (age >= min_age) & (age <= max_age)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        # IRC 32(c)(1)(A)(ii)(III), unchanged since 2020: without a
        # qualifying child, neither filer may be a dependent of another
        # taxpayer. As in the federal credit, a would-be claimant who has no
        # filing requirement and files no return or only for a refund doesn't
        # bar the credit. The IRS prints no such exception in Rule 12 of 2020
        # Publication 596 and prints it in that rule from the 2022 edition. In
        # its volunteer guide for 2020 returns, the IRS applies the exception
        # to the question whether another taxpayer can claim the filer
        # (Publication 4012, page C-3, note 5).
        dependent_elsewhere = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        childless_eligible = (
            tax_unit.any(meets_age_requirements & is_filer_or_spouse)
            & ~dependent_elsewhere
        )
        return has_child | childless_eligible
