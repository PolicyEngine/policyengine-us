from policyengine_us.model_api import *


class ut_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Earned Income Tax Credit"
    unit = USD
    documentation = "This credit is a fraction of the federal EITC."
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.earned_income
        federal_eitc = tax_unit("eitc", period)
        return p.rate * federal_eitc
