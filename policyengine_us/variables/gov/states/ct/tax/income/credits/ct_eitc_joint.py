from policyengine_us.model_api import *


class ct_eitc_joint(Variable):
    value_type = float
    entity = Person
    label = "Connecticut Earned Income Tax Credit For Head of Household Filing"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/Schedule-CT-EITC_1222.pdf"
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704e"
    )
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        amt = person.tax_unit("ct_eitc_unit", period)
        is_head = person("is_tax_unit_head", period)
        return amt * is_head
