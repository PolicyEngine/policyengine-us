from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import section_911_gross_exclusion


class tax_unit_is_required_to_file(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file federal taxes"
    documentation = """
    Whether this tax unit is legally required to file a federal income tax
    return under IRC § 6012, based on gross income thresholds and filing
    status. Under § 6012(c), gross income includes amounts excluded under
    § 911: Form 2555 line 43 when Form 2555 leaf inputs are supplied,
    otherwise the legacy foreign_earned_income_exclusion amount.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6012",
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
        # computed without regard to the section 911 exclusion. That is the
        # gross exclusion on Form 2555 line 43, not the worksheet line 2c
        # stacking amount, which is net of line 44 and worksheet line 2b and
        # includes the line 50 housing deduction.
        section_911_exclusion = section_911_gross_exclusion(tax_unit, period)
        gross_income = add(tax_unit, period, ["irs_gross_income"]) + (
            section_911_exclusion
        )
        p = parameters(period).gov.irs.income.exemption
        exemption_amount = 0 if p.suspended else p.amount

        # (a)(1)(A), (a)(1)(B)
        filing_status = tax_unit("filing_status", period).decode_to_str()
        separate = filing_status == "SEPARATE"
        standard_deduction = tax_unit("standard_deduction", period)
        threshold = where(
            separate,
            exemption_amount,
            standard_deduction + exemption_amount,
        )

        income_over_exemption_amount = gross_income > threshold

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
        head_can_be_claimed = tax_unit("head_is_dependent_elsewhere", period)
        spouse_can_be_claimed = tax_unit("spouse_is_dependent_elsewhere", period)
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
        p_standard = parameters(period).gov.irs.deductions.standard
        aged_or_blind_count = person("is_irs_aged", period).astype(int) + person(
            "is_blind", period
        ).astype(int)
        additional_standard_deduction = aged_or_blind_count * tax_unit.project(
            p_standard.aged_or_blind.amount[tax_unit("filing_status", period)]
        )
        unearned_income_threshold = (
            p_standard.dependent.amount + additional_standard_deduction
        )
        unearned_income_over_threshold = tax_unit.any(
            can_be_claimed & (unearned_income > unearned_income_threshold)
        )

        return income_over_exemption_amount | unearned_income_over_threshold
