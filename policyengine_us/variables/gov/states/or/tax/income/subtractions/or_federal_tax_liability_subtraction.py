from policyengine_us.model_api import *


class or_federal_tax_liability_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR federal tax liability subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        # ORS 316.680(1)(b), 316.685 and 316.695(3).
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
        # Federal tax worksheet, Part A.
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2025.pdf#page=71",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=72",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.subtractions.federal_tax_liability
        )
        # Federal tax worksheet, line 5: federal income tax after nonrefundable
        # credits plus the other taxes on Schedule 2, lines 8, 16 and 17. The
        # worksheet leaves out the net investment income tax (Schedule 2, line
        # 12) and Social Security and Medicare taxes on unreported tips and
        # wages (lines 5 and 6; ORS 316.685(3)(a)).
        tax_before_refundable_credits = tax_unit(
            "income_tax_before_refundable_credits", period
        ) - add(tax_unit, period, ["net_investment_income_tax", "unreported_payroll_tax"])
        # Only the refundable credits the worksheet lists reduce the liability.
        # The earned income credit never does (ORS 316.685(1)(b)).
        refundable_credits = add(tax_unit, period, p.refundable_credits)
        or_federal_income_tax = max_(
            0, tax_before_refundable_credits - refundable_credits
        )
        # limit subtraction based on caps scaled to federal AGI
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        federal_agi = tax_unit("adjusted_gross_income", period)
        cap = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.cap.single.calc(federal_agi),
                p.cap.joint.calc(federal_agi),
                p.cap.head_of_household.calc(federal_agi),
                p.cap.separate.calc(federal_agi),
                p.cap.surviving_spouse.calc(federal_agi),
            ],
        )
        return min_(or_federal_income_tax, cap)
