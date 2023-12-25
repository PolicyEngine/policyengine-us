from policyengine_us.model_api import *


class la_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana personal exemption"
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=101761"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.la.tax.income.exemptions
        return p.personal[filing_status]
