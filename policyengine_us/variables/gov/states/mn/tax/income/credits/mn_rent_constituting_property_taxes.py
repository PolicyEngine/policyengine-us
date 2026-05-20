from policyengine_us.model_api import *


class mn_rent_constituting_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota rent constituting property taxes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.renters
        gross_rent = add(tax_unit, period, ["rent"])
        return round_(gross_rent * p.rent_fraction)
