from policyengine_us.model_api import *


class nd_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/north-dakota-century-code/title-57-taxation/chapter-57-38-income-tax/section-57-38-303-individual-estate-and-trust-income-tax"
        # North Dakota legal code 57-38-30.3.(1)
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        taxable_income = tax_unit("nd_taxable_income", period)
        p = parameters(period).gov.states.nd.tax.income.rates
        return select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.widow.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
            ],
        )
