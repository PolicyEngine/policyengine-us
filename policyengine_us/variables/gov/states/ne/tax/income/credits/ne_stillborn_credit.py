from policyengine_us.model_api import *


class ne_stillborn_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska stillborn child tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE
    reference = "https://nebraskalegislature.gov/FloorDocs/107/PDF/Slip/LB432.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        return stillborn * p.stillborn
