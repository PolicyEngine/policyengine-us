from policyengine_us.model_api import *


class hi_alternative_tax_on_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii alternative tax on capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = "hi_alternative_tax_on_capital_gains_eligible"

    def formula(tax_unit, period, parameters):
        # The alternative tax on capital is computed as the sum of the eligible taxable income
        # multiplied by the normal tax rate or by a flat tax rate.
        eligible_taxable_income = tax_unit(
            "hi_taxable_income_for_alternative_tax", period
        )
        p = parameters(period).gov.states.hi.tax.income
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        normal_tax_rate = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rates.single.calc(eligible_taxable_income),
                p.rates.separate.calc(eligible_taxable_income),
                p.rates.joint.calc(eligible_taxable_income),
                p.rates.widow.calc(eligible_taxable_income),
                p.rates.head_of_household.calc(eligible_taxable_income),
            ],
        )
        taxable_income = tax_unit("hi_taxable_income", period)
        excess_taxable_income = max_(
            0, taxable_income - eligible_taxable_income
        )
        flat_tax_rate = p.alternative_tax.rate * excess_taxable_income
        return flat_tax_rate + normal_tax_rate
