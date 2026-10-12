from policyengine_us.model_api import *


class ga_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.main
        income = tax_unit("ga_taxable_income", period)
        if p.flat_applies:
            return p.flat_rate * income
        # Pre-2024 progressive bracket structure by filing status.
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.SEPARATE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(income),
                p.separate.calc(income),
                p.joint.calc(income),
                p.head_of_household.calc(income),
                p.surviving_spouse.calc(income),
            ],
        )
