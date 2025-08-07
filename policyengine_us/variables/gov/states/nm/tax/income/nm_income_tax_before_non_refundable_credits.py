from policyengine_us.model_api import *


class nm_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        income = tax_unit("nm_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.nm.tax.income.main
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(income),
                p.joint.calc(income),
                p.separate.calc(income),
                p.surviving_spouse.calc(income),
                p.head_of_household.calc(income),
            ],
        )
