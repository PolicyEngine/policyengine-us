from policyengine_us.model_api import *


class ut_recapture_low_inc_housing_credit(Variable):
    """
    Line 30 on Utah 2022 Individual Income Tax return form TC-40. This addition
    is described on form TC-40LIC
    (https://tax.utah.gov/forms/current/tc-40lic.pdf) and allows the filer to
    reapportion parts of the nonrefundable Utah low-income housing credit from
    a previous year filing for up to three years in order to capture the
    maximum amount possible of the credit.
    """

    value_type = float
    entity = TaxUnit
    label = "UT recapture of low-income housing credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
