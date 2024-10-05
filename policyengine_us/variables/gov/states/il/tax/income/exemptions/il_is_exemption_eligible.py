from policyengine_us.model_api import *


class il_is_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether this tax unit is eligible for any exemptions"
    unit = USD
    definition_period = YEAR

    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        cap = parameters(
            period
        ).gov.states.il.tax.income.exemption.income_limit[filing_status]
        return tax_unit("adjusted_gross_income", period) <= cap
