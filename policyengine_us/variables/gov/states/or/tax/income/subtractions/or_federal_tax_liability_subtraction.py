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
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # calculate Oregon concept of federal income tax
        federal_itax = tax_unit("income_tax", period)
        federal_eitc = tax_unit("eitc", period)
        or_federal_income_tax = max_(0, federal_itax + federal_eitc)
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
                filing_status == status.WIDOW,
            ],
            [
                p.single.calc(federal_agi),
                p.joint.calc(federal_agi),
                p.head_of_household.calc(federal_agi),
                p.separate.calc(federal_agi),
                p.widow.calc(federal_agi),
            ],
        )
        return min_(or_federal_income_tax, cap)
