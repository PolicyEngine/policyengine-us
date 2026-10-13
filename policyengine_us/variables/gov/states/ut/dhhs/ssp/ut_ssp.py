from policyengine_us.model_api import *


class ut_ssp(Variable):
    value_type = float
    entity = Person
    label = "Utah State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    defined_for = "ut_ssp_eligible"
    # Utah administers and issues this payment itself, not through SSA
    # (Manual 661, "The Payment Process").
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R414-306-6",
        "https://oepmanuals.dhhs.utah.gov/600_Program_Benefits/661_Fifteen_Dollar_State_Supplemental_Payment_%28SSP%29.htm",
    )
    adds = ["gov.states.ut.dhhs.ssp.amount"]
