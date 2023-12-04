from policyengine_us.model_api import *


class ct_amt_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-6251_1222.pdf#page=1"  # line 5

    adds = [
        "amt_income",
        "ct_amt_subtractions",
    ]  # Line 3 = Line 1 + Line 2
    subtracts = ["ct_amt_subtractions"]  # Line 4


# Comments:
# rename ct_amt_income_additions to ct_amt_additions; same for subtarctions


# rename this file to ct_amt_income

