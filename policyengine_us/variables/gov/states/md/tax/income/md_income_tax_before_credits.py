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

        # Calculate regular income tax based on filing status
        p = parameters(period).gov.states.md.tax.income
        regular_income_tax = select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
            ],
            [
                p.rates.single.calc(taxable_income),
                p.rates.separate.calc(taxable_income),
                p.rates.joint.calc(taxable_income),
                p.rates.head_of_household.calc(taxable_income),
                p.rates.surviving_spouse.calc(taxable_income),
            ],
        )

        # Add capital gains surtax if applicable
        if p.capital_gains.surtax_applies:
            capital_gains_surtax = tax_unit("md_capital_gains_surtax", period)
            return regular_income_tax + capital_gains_surtax
        return regular_income_tax
