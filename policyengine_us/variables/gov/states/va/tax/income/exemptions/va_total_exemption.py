from policyengine_us.model_api import *


class va_total_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia total exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.exemptions
        personal_exemption = p.personal
        age_blind_exemption = p.age_blind
        total_exemption = p.personal + p.age_blind
        return total_exemption
