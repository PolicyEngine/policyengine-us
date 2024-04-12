from policyengine_us.model_api import *


class mt_income_tax_before_non_refundable_credits_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        income = add(tax_unit, period, ["mt_taxable_income_joint"]) - add(
            tax_unit, period, ["long_term_capital_gains"]
        )
        capital_gains_tax = add(
            tax_unit, period, ["mt_capital_gains_tax_joint"]
        )
        p = parameters(period).gov.states.mt.tax.income.main
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(income) + capital_gains_tax,
                p.joint.calc(income) + capital_gains_tax,
                p.head_of_household.calc(income) + capital_gains_tax,
                p.separate.calc(income) + capital_gains_tax,
                p.widow.calc(income) + capital_gains_tax,
            ],
        )
