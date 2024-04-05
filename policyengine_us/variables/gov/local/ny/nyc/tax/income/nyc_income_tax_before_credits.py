from policyengine_us.model_api import *


class nyc_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("nyc_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        rates = parameters(period).gov.local.ny.nyc.tax.income.rates
        return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
                filing_status == filing_statuses.SEPARATE,
            ],
            [
                rates.single.calc(taxable_income),
                rates.joint.calc(taxable_income),
                rates.head_of_household.calc(taxable_income),
                rates.widow.calc(taxable_income),
                rates.separate.calc(taxable_income),
            ],
        )
