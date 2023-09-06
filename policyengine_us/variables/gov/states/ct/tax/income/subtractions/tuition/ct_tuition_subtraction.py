from policyengine_us.model_api import *


class ct_tuition_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut tuition subtraction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701a"
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.subtractions.tuition
        filing_status = tax_unit("filing_status", period)
        max_amount = p.max_amount[filing_status]
        tuition = add(tax_unit, period, ["qualified_tuition_expenses"])
        return min_(tuition, max_amount)
