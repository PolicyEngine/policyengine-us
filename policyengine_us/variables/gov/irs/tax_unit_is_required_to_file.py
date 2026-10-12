from policyengine_us.model_api import *


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
    standard deduction test in every year.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6012",
        # From 2026 (and before 2018): section 6012(a)(1)(A) and (B), and
        # Chart A of the Form 1040 instructions for 2017, the last year it
        # governed.
        "https://www.law.cornell.edu/uscode/text/26/6012#a_1",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2017.pdf#page=8",
        # 2018 to 2025: section 6012(f).
        "https://www.law.cornell.edu/uscode/text/26/6012#f",
        # A filer who can be claimed as a dependent: section 6012(a)(1)(C)(i)
        # and (f)(2)(D) (the section above), the section 63(c)(5) limited
        # standard deduction, and Publication 501, Table 2 (Chart B of the
        # Form 1040 instructions).
        "https://www.law.cornell.edu/uscode/text/26/63#c_5",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4",
        # Gross income counts amounts excluded under section 911.
        "https://www.law.cornell.edu/uscode/text/26/6012#c",
    )

    def formula(tax_unit, period, parameters):
        # Section 6012(c): for the filing requirement, gross income is
        # computed without regard to the section 911 exclusion.
        section_911_exclusion = tax_unit("foreign_earned_income_exclusion", period)
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
        # equal to it requires a return. A married individual filing
        # separately has no exception. The WFTCA contributed reform's bonus
        # guaranteed deduction is an increase to the basic standard deduction
        # (zero unless that reform is on).
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
                unearned_income += max_(0, add(person, period, [source]))
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
