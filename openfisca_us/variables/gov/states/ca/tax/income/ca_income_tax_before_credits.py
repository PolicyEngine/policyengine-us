from openfisca_us.model_api import *


class ca_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA income tax before credits"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/Search/Home/Confirmation"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("ca_taxable_income", period)
        p = parameters(period).gov.states.ca.tax.income.rates

        statuses = filing_status.possible_values

        return select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
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
