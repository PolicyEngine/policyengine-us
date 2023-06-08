from policyengine_us.model_api import *


class la_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana qualified dependents exemption"
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=101761"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        dependents = tax_unit("tax_unit_dependents", period)
        return (
            dependents
            * parameters(period).gov.states.la.tax.income.exemptions.dependent
        )
