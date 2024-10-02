from policyengine_us.model_api import *


class ut_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Earned Income Tax Credit"
    unit = USD
    documentation = "This credit is a fraction of the federal EITC."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1044.html?v=C59-10-S1044_2022050420220504"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.earned_income
        federal_eitc = tax_unit("eitc", period)
        return p.rate * federal_eitc
