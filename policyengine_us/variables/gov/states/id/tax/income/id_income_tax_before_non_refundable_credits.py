from policyengine_us.model_api import *


class id_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        income = tax_unit("id_taxable_income", period)
        rates = parameters(period).gov.states.id.tax.income.main
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                rates.single.calc(income),
                rates.joint.calc(income),
                rates.separate.calc(income),
                rates.surviving_spouse.calc(income),
                rates.head_of_household.calc(income),
            ],
        )
