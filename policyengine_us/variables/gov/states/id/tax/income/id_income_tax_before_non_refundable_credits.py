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

        return select_filing_status_value(filing_status, rates, income)
