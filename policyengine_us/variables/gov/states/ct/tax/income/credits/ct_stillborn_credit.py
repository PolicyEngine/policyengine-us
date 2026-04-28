from policyengine_us.model_api import *


class ct_stillborn_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut stillborn credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704i"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.credits
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        return stillborn * p.stillborn
