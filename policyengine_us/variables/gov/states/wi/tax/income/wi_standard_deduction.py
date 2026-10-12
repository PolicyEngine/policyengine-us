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
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        fstatus = tax_unit("filing_status", period)
        agi = tax_unit("wi_agi", period)
        return wi_standard_deduction_for_income(agi, fstatus, parameters, period)
