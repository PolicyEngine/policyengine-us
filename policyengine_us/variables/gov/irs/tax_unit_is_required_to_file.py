from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import section_911_gross_exclusion


class tax_unit_is_required_to_file(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file federal taxes"
    documentation = """
    Whether this tax unit is legally required to file a federal income tax
    return under IRC § 6012, based on gross income thresholds and filing
    status. For 2018 to 2025, section 6012(f) compares gross income with the
    standard deduction. In other years, section 6012(a)(1) compares it with
    the basic standard deduction plus the additions for age, but not
    blindness, and gross income equal to that amount requires a return. A
    tax unit whose head or spouse can be claimed as a dependent keeps the
    standard deduction test in every year. Under section 6012(c), both
    tests count gross section 911 exclusions: Form 2555 line 43 when leaf
    inputs are supplied, otherwise the nonnegative legacy
    foreign_earned_income_exclusion amount.
    """
    definition_period = YEAR
    reference = (
        # Section 6012(f) for 2018 to 2025, and 6012(a)(1)(A) and (B) in other
        # years.
        "https://www.law.cornell.edu/uscode/text/26/6012",
        # Chart A of the Form 1040 instructions for 2017, the last year
        # section 6012(a)(1) governed.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2017.pdf#page=8",
        # Separate filers with a zero exemption amount, and the IRS's $5.
        "https://www.taxpayeradvocate.irs.gov/news/nta-blog/ntablog-irs-publication-error-may-have-caused-certain-married-taxpayers-filing-separately-to-fail-to-file-required-tax-returns/2019/12/",
        # A filer who can be claimed as a dependent: section 6012(a)(1)(C)(i)
        # and (f)(2)(D) (the section above), the section 63(c)(5) limited
        # standard deduction, and Publication 501, Table 2 (Chart B of the
        # Form 1040 instructions).
        "https://www.law.cornell.edu/uscode/text/26/63#c_5",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4",
        # Gross income counts amounts excluded under section 911.
        "https://www.law.cornell.edu/uscode/text/26/6012#c",
        # Chart A: gross income includes income from sources outside the
        # United States "even if you can exclude part or all of it".
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
        # Form 2555 line 43: the line 36 and line 42 exclusions.
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        # Section 6012(c): for the filing requirement, gross income is
        # computed without regard to the section 911 exclusion in every year,
        # including the section 6012(a)(1) threshold from 2026. That is the
        # gross exclusion on Form 2555 line 43, not the worksheet line 2c
        # stacking amount, which is net of line 44 and worksheet line 2b and
        # includes the line 50 housing deduction.
        section_911_exclusion = section_911_gross_exclusion(tax_unit, period)
        gross_income = add(tax_unit, period, ["irs_gross_income"]) + (
            section_911_exclusion
        )
        p = parameters(period).gov.irs
        exemption_amount = (
            0 if p.income.exemption.suspended else p.income.exemption.amount
        )
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        head_can_be_claimed = tax_unit("head_is_dependent_elsewhere", period)
        spouse_can_be_claimed = tax_unit("spouse_is_dependent_elsewhere", period)

        # Section 6012(f), for 2018 to 2025: no return is required when gross
        # income does not exceed the standard deduction, which includes the
        # additional standard deduction for age and for blindness. A married
        # individual filing separately must file with any gross income.
        threshold = where(
            separate,
            exemption_amount,
            tax_unit("standard_deduction", period) + exemption_amount,
        )
        income_over_standard_deduction = gross_income > threshold

        # Section 6012(a)(1)(A) and (B), from 2026 (and before 2018): no return
        # is required when gross income is less than the exemption amount for
        # each spouse plus the basic standard deduction, raised by one
        # additional standard deduction for each spouse aged 65 or older
        # (section 63(f)(1)). Blindness does not raise it, and gross income
        # equal to it requires a return. The WFTCA contributed reform's bonus
        # guaranteed deduction is an increase to the basic standard deduction
        # (zero unless that reform is on).
        #
        # A married individual filing separately has no exception. With an
        # exemption amount of zero, (A) read literally reaches even an
        # individual with no gross income; the National Taxpayer Advocate read
        # the 2018 to 2025 rule that way, and the IRS set $5 as relief. As for
        # 2018 to 2025, the model requires a return only for positive gross
        # income (decision d1403).
        aged_count = tax_unit("aged_head", period).astype(int) + tax_unit(
            "aged_spouse", period
        ).astype(int)
        basic_threshold = (
            exemption_amount * tax_unit("head_spouse_count", period)
            + tax_unit("basic_standard_deduction", period)
            + tax_unit("bonus_guaranteed_deduction", period)
            + aged_count * p.deductions.standard.aged_or_blind.amount[filing_status]
        )
        income_at_least_basic_threshold = (gross_income > 0) & (
            gross_income >= where(separate, exemption_amount, basic_threshold)
        )

        # A tax unit whose head or spouse can be claimed as a dependent keeps
        # the standard deduction test in every year. From 2026 it is
        # (a)(1)(C)(i)(II), and it is what Chart B applies under (a)(1); the
        # (A) threshold, which leaves out blindness and requires a return at
        # equality, is not applied to these filers (decision d1395).
        if p.income.filing_requirement.standard_deduction_rule.applies:
            income_over_threshold = income_over_standard_deduction
        else:
            income_over_threshold = where(
                head_can_be_claimed | spouse_can_be_claimed,
                income_over_standard_deduction,
                income_at_least_basic_threshold,
            )

        # A filer who can be claimed as a dependent on another return (an
        # individual described in section 63(c)(5)) must also file when their
        # income other than earned income is over the section 63(c)(5)(A)
        # amount plus their own additional standard deduction for age or
        # blindness: section 6012(a)(1)(C)(i)(I) and Publication 501, Table 2.
        # On a joint return the test applies to each spouse who can be claimed.
        # Section 6012(f)(2)(D), which governs joint returns for 2018 to 2025,
        # names the section 63(c)(5)(A) amount alone; Table 2 adds the
        # additional standard deduction, and this follows Table 2 (open as
        # decision d1395). Nobody else has an unearned income test.
        #
        # Table 2's other two tests need no code here. The standard deduction
        # in the threshold above is already the limited one for these filers
        # (basic_standard_deduction): the greater of the section 63(c)(5)(A)
        # amount or earned income plus the section 63(c)(5)(B) amount, capped
        # at the regular amount, plus the additional standard deduction. That
        # is Table 2's gross income test, and earned income over the regular
        # amount plus the additional standard deduction always meets it.
        person = tax_unit.members
        can_be_claimed = (
            person("is_tax_unit_head", period) & tax_unit.project(head_can_be_claimed)
        ) | (
            person("is_tax_unit_spouse", period)
            & tax_unit.project(spouse_can_be_claimed)
        )
        # Income other than earned income: every gross income source except
        # the earned income sources of the IRS dependent worksheet (wages,
        # business income and farm income). As in irs_gross_income, a loss in
        # one source does not reduce the total.
        earned_income_sources = parameters(
            period
        ).gov.irs.income.filing_requirement.dependent.earned_income_sources
        unearned_income = 0
        for source in parameters(period).gov.irs.gross_income.sources:
            if source not in earned_income_sources:
                source_income = add(person, period, [source])
                if source == "taxable_disability_benefits":
                    # Before minimum retirement age, disability pensions go
                    # on Form 1040 line 1h (included in worksheet line 1z).
                    # Only the remaining taxable disability pay is unearned.
                    source_income = source_income - person(
                        "earned_disability_benefits", period
                    )
                unearned_income += max_(0, source_income)
        p_standard = p.deductions.standard
        aged_or_blind_count = person("is_irs_aged", period).astype(int) + person(
            "is_blind", period
        ).astype(int)
        additional_standard_deduction = aged_or_blind_count * tax_unit.project(
            p_standard.aged_or_blind.amount[filing_status]
        )
        unearned_income_threshold = (
            p_standard.dependent.amount + additional_standard_deduction
        )
        unearned_income_over_threshold = tax_unit.any(
            can_be_claimed & (unearned_income > unearned_income_threshold)
        )

        return income_over_threshold | unearned_income_over_threshold
