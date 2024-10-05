from policyengine_us.model_api import *


class ct_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/Schedule-CT-EITC_1222.pdf"
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704e"
    )
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        rate = parameters(period).gov.states.ct.tax.income.credits.eitc.match
        return federal_eitc * rate
