from policyengine_us.model_api import *


def wi_standard_deduction_for_income(income, filing_status, parameters, period):
    # Wisconsin standard deduction (Form 1 line 8) as a function of WI income.
    # Factored out of the variable below so the retirement-income-exclusion
    # path can look the deduction up on income reduced by the Schedule SB
    # line-16 subtraction (the phaseout otherwise stays keyed to the higher
    # pre-subtraction income).
    deduction = parameters(period).gov.states.wi.tax.income.deductions
    statuses = filing_status.possible_values
    max_amount = deduction.standard.max[filing_status]
    phase_out_amount = select(
        [
            filing_status == statuses.SINGLE,
            filing_status == statuses.JOINT,
            filing_status == statuses.SURVIVING_SPOUSE,
            filing_status == statuses.SEPARATE,
            filing_status == statuses.HEAD_OF_HOUSEHOLD,
        ],
        [
            deduction.standard.phase_out.single.calc(income),
            deduction.standard.phase_out.joint.calc(income),
            deduction.standard.phase_out.joint.calc(income),
            deduction.standard.phase_out.separate.calc(income),
            deduction.standard.phase_out.head_of_household.calc(income),
        ],
    )
    return max_(0, max_amount - phase_out_amount)


def wi_dependent_standard_deduction_limit(tax_unit, period, parameters):
    # Wis. Stat. 71.05(22)(f): for a taxpayer whom another person can claim
    # as a dependent, the standard deduction is the lesser of the ordinary
    # deduction and the greater of $500 or earned income (IRC 911(d)(2)) plus
    # $250, both indexed "in the manner prescribed by sections 1 (f) (3) to
    # (6) and 63 (c) (4)" of the IRC, so they equal the federal amounts (Form
    # 1 instructions: $1,100 + $350 in 2021 through $1,350 + $450 in 2025).
    # The Form 1 worksheet applies when "you (or your spouse if filing a
    # joint return) can be claimed", using the return's earned income.
    # Returns infinity when no filer can be claimed.
    p = parameters(period).gov.irs.deductions.standard.dependent
    earned_income = max_(tax_unit("tax_unit_earned_income", period), 0)
    limit = max_(p.amount, earned_income + p.additional_earned_income)
    filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
    return where(filer_is_dependent, limit, np.inf)


class wi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf",
        # Standard Deduction Table (keyed to WI income, line 7) and the statute, corroborating the phaseout:
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=35",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/22",
        # Standard Deduction Worksheet for Dependents
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=15",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        fstatus = tax_unit("filing_status", period)
        agi = tax_unit("wi_agi", period)
        standard_deduction = wi_standard_deduction_for_income(
            agi, fstatus, parameters, period
        )
        return min_(
            standard_deduction,
            wi_dependent_standard_deduction_limit(tax_unit, period, parameters),
        )
