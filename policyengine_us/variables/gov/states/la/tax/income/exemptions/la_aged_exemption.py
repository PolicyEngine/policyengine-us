from policyengine_us.model_api import *


class la_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana aged exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.exemptions.aged
        aged_head = (tax_unit("age_head", period) >= p.age_threshold).astype(int)
        aged_spouse = (tax_unit("age_spouse", period) >= p.age_threshold).astype(int)
        return aged_head * p.amount + aged_spouse * p.amount