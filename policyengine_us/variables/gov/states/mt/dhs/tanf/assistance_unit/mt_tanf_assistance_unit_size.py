from policyengine_us.model_api import *


class mt_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) assistance unit size"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.208"
    defined_for = StateCode.MT

    adds = [
        "mt_tanf_payment_eligible_child",
        "mt_tanf_payment_eligible_parent",
    ]
