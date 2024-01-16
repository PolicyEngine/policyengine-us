from policyengine_us.model_api import *


class vt_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6066/" # b
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=35"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        