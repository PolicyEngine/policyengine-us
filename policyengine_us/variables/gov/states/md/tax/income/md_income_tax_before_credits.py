from policyengine_us.model_api import *


class md_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        taxable_income = tax_unit("md_taxable_income", period)
        # Calculate for each of the filing statuses and return the appropriate one.
        p = parameters(period).gov.states.md.tax.income.rates
        return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.WIDOW,
            ],
            [
                p.single.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.head.calc(taxable_income),
                p.widow.calc(taxable_income),
            ],
        )
