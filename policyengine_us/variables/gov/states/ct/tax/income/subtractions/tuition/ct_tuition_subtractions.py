from policyengine_us.model_api import *


class ct_tuition_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CT tuition subtractions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701a"
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.subtractions.tuition.max_amount
        filing_status = tax_unit("filing_status", period)
        max_amount = p[filing_status]
        tuition = add(tax_unit, period, ["qualified_tuition_expenses"])
        subtraction = min(tuition, max_amount)
        return subtraction
