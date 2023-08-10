from policyengine_us.model_api import *


class ct_eitc_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Connecticut Earned Income Tax Credit For Married But Separate Filing"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/Schedule-CT-EITC_1222.pdf"
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704e"
    )
    defined_for = StateCode.CT

    def formula(person, period, parameters):
        amt = person.tax_unit("ct_eitc_unit", period)
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        separate_status = filing_status == filing_statuses.SEPARATE
        agi_separate = tax_unit("adjusted_gross_income_person", period)
        agi_joint = tax_unit("adjusted_gross_income", period)
        agi_frac = agi_separate / agi_joint
        return amt * agi_frac
