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
        # if no subsidized: (upper cap - lower cap)/(upper cap - income) * 0.1 * number of rent month/12 * fair market rent * 0.5 if shared rent
        # if subsidized:  combined amount = subsidized amount + non-subsidized amount
        # subsidized amount: actual pay rent amount * 0.1 * subsidzed mouth/number of rent month
        # non-subsidized amount: (number of rent month - subsized month)/number of rent month * fair market rent
        # result: (upper cap - lower cap)/(upper cap - income) * number of rent month/12 * combined amount
