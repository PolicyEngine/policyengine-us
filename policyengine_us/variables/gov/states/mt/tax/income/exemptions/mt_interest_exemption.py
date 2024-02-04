from policyengine_us.model_api import *


class mt_interest_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana interest exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    adds = ["mt_interest_exemption_person"]
