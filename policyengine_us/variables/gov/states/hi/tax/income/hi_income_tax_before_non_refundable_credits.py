from policyengine_us.model_api import *


class hi_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax before non-refundable credits"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    # Hawaii Tax Rate Schedules
    reference = " https://tax.hawaii.gov/forms/d_18table-on/d_18table-on_p13/"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("hi_taxable_income", period)
        p = parameters(period).gov.states.hi.tax.income.rates

        statuses = filing_status.possible_values

        income_tax = select(
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
        alternative_tax = tax_unit(
            "hi_alternative_tax_on_capital_gains", period
        )

        alternative_tax_eligible = tax_unit(
            "hi_alternative_tax_on_capital_gains_eligible", period
        )
        return where(
            alternative_tax_eligible,
            min_(income_tax, alternative_tax),
            income_tax,
        )
