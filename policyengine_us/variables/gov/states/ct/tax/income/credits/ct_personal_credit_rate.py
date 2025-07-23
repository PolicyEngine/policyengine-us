from policyengine_us.model_api import *


class ct_personal_credit_rate(Variable):
    value_type = float
    entity = TaxUnit
    unit = "\1"
    label = "Connecticut personal credit rate"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ct_agi", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.agi

        return select_filing_status_value(
            filing_status,
            p,
            agi,
            right=True,
        )
