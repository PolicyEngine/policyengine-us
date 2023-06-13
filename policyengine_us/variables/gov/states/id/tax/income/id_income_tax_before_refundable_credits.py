from policyengine_us.model_api import *


class id_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho income tax before refundable credits"
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
                filing_status == status.WIDOW
            ],
            [
                rates.single.calc(income),
                rates.married.calc(income),
                
            ],
        )
