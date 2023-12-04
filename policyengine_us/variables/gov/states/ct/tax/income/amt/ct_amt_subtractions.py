from policyengine_us.model_api import *


class ct_amt_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut subtractions from federal alternative minimum taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-6251_1222.pdf#page=5"  # line 4

    adds = "gov.states.ct.tax.income.adjustments.subtractions_adjustments"
