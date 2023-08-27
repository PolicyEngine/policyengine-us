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
        filing_status = person.tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        separate_status = filing_status == filing_statuses.SEPARATE
        agi_separate = person("adjusted_gross_income_person", period)
        agi_joint = person.tax_unit("adjusted_gross_income", period)
        agi_frac = np.zeros_like(agi_joint)
        mask = agi_joint != 0
        agi_frac[mask] = agi_separate[mask] / agi_joint[mask]
        return amt * agi_frac
