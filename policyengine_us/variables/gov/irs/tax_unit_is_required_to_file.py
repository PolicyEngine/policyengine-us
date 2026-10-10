from policyengine_us.model_api import *

# Gross income sources that are earned income (wages and self-employment
# income, as in earned_income). The rest of gross income is unearned income
# for the dependent filing requirement.
EARNED_GROSS_INCOME_SOURCES = (
    "irs_employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
)


class tax_unit_is_required_to_file(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file federal taxes"
    documentation = """
    Whether this tax unit is legally required to file a federal income tax
    return under IRC § 6012, based on gross income thresholds and filing
    status, and on the unearned income of a head or spouse who can be
    claimed as a dependent on another return.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6012",
        # Gross income counts amounts excluded under section 911.
        "https://www.law.cornell.edu/uscode/text/26/6012#c",
        # Special rule for 2018 through 2025, including the joint return
        # condition in (f)(2)(D).
        "https://www.law.cornell.edu/uscode/text/26/6012#f",
        # Form 1040 instructions, Chart B—For Children and Other Dependents.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        # Section 6012(c): for the filing requirement, gross income is
        # computed without regard to the section 911 exclusion.
        section_911_exclusion = tax_unit("foreign_earned_income_exclusion", period)
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

        # A head or spouse who can be claimed as a dependent on another
        # return must file when their own unearned income exceeds the
        # dependent standard deduction floor of section 63(c)(5)(A) plus
        # their own additional standard deduction for age or blindness
        # (section 6012(a)(1)(C)(i)(I); Chart B). For 2018 through 2025,
        # section 6012(f)(2)(D) withholds the joint return exception when
        # either spouse has unearned income above the floor alone.
        # From 2026, section 6012(a)(1) also withholds the joint return
        # exception from the spouse of such a filer, whatever that spouse's
        # income. The model does not apply that rule; the filing charts did
        # not reflect it when it was last in force, in 2017.
        irs = parameters(period).gov.irs
        standard = irs.deductions.standard
        person = tax_unit.members
        # Gross income adds the positive part of each source, so subtract
        # the positive part of each earned source. Excluded foreign earnings
        # are earned income and are in neither amount.
        unearned_income = person("irs_gross_income", period)
        for source in EARNED_GROSS_INCOME_SOURCES:
            if source in irs.gross_income.sources:
                unearned_income = unearned_income - max_(0, person(source, period))
        claimable_filer = person("is_tax_unit_head_or_spouse", period) & person(
            "claimed_as_dependent_on_another_return", period
        )
        aged = person("age", period) >= standard.aged_or_blind.age_threshold
        blind = person("is_blind", period)
        additional_amount = standard.aged_or_blind.amount[
            tax_unit("filing_status", period)
        ]
        joint_under_special_rule = (
            irs.income.filing_requirement.special_rule.in_effect
            & (filing_status == "JOINT")
        )
        additional_standard_deduction = where(
            joint_under_special_rule, 0, additional_amount
        )
        unearned_income_threshold = standard.dependent.amount + tax_unit.project(
            additional_standard_deduction
        ) * (aged.astype(int) + blind.astype(int))
        dependent_unearned_income_over_threshold = tax_unit.any(
            claimable_filer & (unearned_income > unearned_income_threshold)
        )

        return income_over_exemption_amount | dependent_unearned_income_over_threshold
