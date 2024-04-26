from policyengine_us.model_api import *


class mt_income_tax_before_non_refundable_credits_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main
        taxable_income = add(tax_unit, period, ["mt_taxable_income_joint"])
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        if p.capital_gains.in_effect:
            capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
            taxable_income = max_(taxable_income - capital_gains, 0)
            capital_gains_tax = add(
                tax_unit, period, ["mt_capital_gains_tax_joint"]
            )
        else:
            capital_gains_tax = 0

        regular_tax = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.widow.calc(taxable_income),
            ],
        )
        return regular_tax + capital_gains_tax
