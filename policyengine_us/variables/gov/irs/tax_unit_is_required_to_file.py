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
    blindness, and gross income equal to that amount requires a return. From
    2026, with a zero exemption amount, a married individual filing separately
    must file even with no gross income.
    That test applies to every filer, including one who can be claimed as a
    dependent (with the section 63(c)(5) limited basic standard deduction),
    and section 6012(a)(1)(C) adds that filer's unearned income and standard
    deduction tests. Under (a)(1), a joint return whose head or spouse can be
    claimed loses the (A)(iv) exception for the other spouse, who must file
    with own gross income at or above the exemption amount, and a filer whose
    standard deduction is zero under section 63(c)(6) loses the (A)
    exception (section 6012(a)(1)(C)(ii)). Under section 6012(c), the
    tax-unit tests count gross section 911 exclusions: Form 2555 line 43 when
    leaf inputs are supplied, otherwise the nonnegative legacy
    foreign_earned_income_exclusion amount. The (A)(iv) own gross income test
    doesn't, because PE-US computes the exclusion only per tax unit.
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
        # exemption amount of zero, (A) reaches even an individual with no
        # gross income, since no gross income is "less than" zero.
        # For a filer who can be claimed as a dependent, basic_standard_deduction
        # is already the section 63(c)(5) limited amount.
        aged_count = tax_unit("aged_head", period).astype(int) + tax_unit(
            "aged_spouse", period
        ).astype(int)
        basic_threshold = (
            exemption_amount * tax_unit("head_spouse_count", period)
            + tax_unit("basic_standard_deduction", period)
            + tax_unit("bonus_guaranteed_deduction", period)
            + aged_count * p.deductions.standard.aged_or_blind.amount[filing_status]
        )
        # Section 6012(a)(1)(C)(ii): the (A) exception does not apply "to any
        # individual ... for whom the standard deduction is zero under section
        # 63(c)(6)". separate_filer_itemizes is PE-US's only 63(c)(6) path, so
        # the threshold falls to the exemption amount, without the age
        # addition, whatever the filing status.
        no_exception = separate | tax_unit("separate_filer_itemizes", period)
        income_at_least_basic_threshold = gross_income >= where(
            no_exception, exemption_amount, basic_threshold
        )

        # Section 6012(a)(1)(A)(iv), the joint-return exception, "shall not
        # apply if for the taxable year ... any other taxpayer is entitled to
        # an exemption for such spouse under section 151(c)". So on a joint
        # return, the spouse of a head or spouse who can be claimed loses
        # (iv). That spouse then has no exception and must file if their own
        # gross income equals or exceeds the exemption amount (zero from
        # 2026). When both can be claimed, both lose (iv). Own gross income is
        # person-level irs_gross_income alone: the section 911 exclusion is
        # computed only per tax unit (policyengine_us/tools/section_911.py),
        # so it can't be split between the spouses here.
        #
        # (iv) also applies only if the spouses "at the close of the taxable
        # year, had the same household as their home". PE-US has no year-end
        # household input and puts a tax unit in one household, so the model
        # treats the spouses of a joint return as sharing one.
        #
        # The separate-return half of the exclusion needs no code: a married
        # individual filing separately already has no exception.
        person = tax_unit.members
        joint = filing_status == filing_status.possible_values.JOINT
        loses_joint_exception = tax_unit.project(joint) & (
            (
                person("is_tax_unit_head", period)
                & tax_unit.project(spouse_can_be_claimed)
            )
            | (
                person("is_tax_unit_spouse", period)
                & tax_unit.project(head_can_be_claimed)
            )
        )
        own_gross_income_at_least_exemption = tax_unit.any(
            loses_joint_exception
            & (person("irs_gross_income", period) >= exemption_amount)
        )

        # Under (a)(1), (C) withdraws the (A) exception from a filer who can
        # be claimed as a dependent in further cases; it does not replace
        # (A) for that filer. So the (A) and (B) threshold binds every filer,
        # and (C)(i)(II), gross income over the standard deduction, is added
        # for a tax unit whose head or spouse can be claimed. Before 2018 this
        # formula uses the full exemption amount in the (C)(i)(II) threshold,
        # the (A) threshold and the own gross income test. (C)(i)(II) names no
        # exemption amount, and section 6012(a)(1)(D)(ii) sets it to zero for
        # an individual described in section 151(d)(2), so before 2018 the
        # formula can excuse a claimable filer the statute requires to file.
        # (C)(i)(I), the unearned income test, is below.
        if p.income.filing_requirement.standard_deduction_rule.applies:
            income_over_threshold = income_over_standard_deduction
        else:
            income_over_threshold = (
                income_at_least_basic_threshold
                | own_gross_income_at_least_exemption
                | (
                    (head_can_be_claimed | spouse_can_be_claimed)
                    & income_over_standard_deduction
                )
            )

        # A filer who can be claimed as a dependent on another return (an
        # individual described in section 63(c)(5)) must also file when their
        # income other than earned income is over the section 63(c)(5)(A)
        # amount plus their own additional standard deduction for age or
        # blindness: section 6012(a)(1)(C)(i)(I) and Publication 501, Table 2.
        # On a joint return the test applies to each spouse who can be claimed.
        # For 2018 to 2025, section 6012(f)(2)(D) sets the joint return test
        # at "the amount in effect under section 63(c)(5)(A)" alone, with no
        # addition for age or blindness, so a claimable spouse aged 65 or
        # blind must file with more than that amount of income other than
        # earned income. Chart B conflicts with the statute: it adds the
        # additional standard deduction ($2,950 rather than $1,350 for 2025).
        # The model follows the statute.
        # For an unmarried filer, section 6012(f)(1) has no separate unearned
        # income test, and Table 2's test with the addition is already implied
        # by the gross income test against the limited standard deduction.
        # Nobody else has an unearned income test.
        #
        # Table 2's other two tests need no code here. The standard deduction
        # in the threshold above is already the limited one for these filers
        # (basic_standard_deduction): the greater of the section 63(c)(5)(A)
        # amount or earned income plus the section 63(c)(5)(B) amount, capped
        # at the regular amount, plus the additional standard deduction. That
        # is Table 2's gross income test, and earned income over the regular
        # amount plus the additional standard deduction always meets it.
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
        statutory_joint_test = (
            joint & p.income.filing_requirement.standard_deduction_rule.applies
        )
        unearned_income_threshold = p_standard.dependent.amount + where(
            tax_unit.project(statutory_joint_test),
            0,
            additional_standard_deduction,
        )
        unearned_income_over_threshold = tax_unit.any(
            can_be_claimed & (unearned_income > unearned_income_threshold)
        )

        return income_over_threshold | unearned_income_over_threshold
