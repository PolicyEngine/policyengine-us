from policyengine_us.model_api import *


class or_federal_tax_liability_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR federal tax liability subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=71",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.800
        # 2025 Publication OR-17, federal tax worksheet, PDF pages 71-72
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2025.pdf#page=71",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # calculate Oregon concept of federal income tax
        federal_itax = tax_unit("income_tax", period)
        federal_eitc = tax_unit("eitc", period)
        # The federal tax worksheet starts from Form 1040 line 22 and does
        # not subtract the section 1341 credit (Schedule 3, line 13b).
        claim_of_right_credit = tax_unit("claim_of_right_credit", period)
        or_federal_income_tax = max_(
            0, federal_itax + federal_eitc + claim_of_right_credit
        )
        # limit subtraction based on caps scaled to federal AGI
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.subtractions.federal_tax_liability.cap
        )
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
                p.single.calc(federal_agi),
                p.joint.calc(federal_agi),
                p.head_of_household.calc(federal_agi),
                p.separate.calc(federal_agi),
                p.surviving_spouse.calc(federal_agi),
            ],
        )
        return min_(or_federal_income_tax, cap)
