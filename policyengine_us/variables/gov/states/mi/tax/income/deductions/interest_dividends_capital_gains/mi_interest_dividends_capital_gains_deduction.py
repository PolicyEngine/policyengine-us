from policyengine_us.model_api import *


class mi_interest_dividends_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan interest, dividends, and capital gains deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan interest, dividends, and capital gains deduction of qualifying age."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (1)(p)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16",
    )
    defined_for = "mi_interest_dividends_capital_gains_deduction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.interest_dividends_capital_gains

        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members

        # Senior citizens may subtract interest, dividends, and capital gains included in AGI.
        income = add(tax_unit, period, p.income_types)
        # The maximum amount of the deduction must be reduced by any deduction for
        # Military (including Michigan National Guard) retirement benefits
        # Public and private retirement and pension benefits
        # Amount used for the federal credit for the elderly and totally and permanently disabled
        reductions_pay = add(
            person,
            period,
            ["military_retirement_pay", "taxable_pension_income"],
        )
        elderly_disabled_credit = tax_unit("elderly_disabled_credit", period)

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        reductions = (
            tax_unit.sum(reductions_pay * is_head_or_spouse)
            + elderly_disabled_credit
        )
        reduced_amount = max_(0, p.amount[filing_status] - reductions)

        return min_(reduced_amount, income)
