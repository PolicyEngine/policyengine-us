from policyengine_us.model_api import *


class vt_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont child care subsidies"
    documentation = (
        "What Vermont's child care subsidy saves the family. Since December 17, "
        "2023 the state's payment to the provider (vt_ccfap) can exceed the "
        "provider's charge; the family keeps paying its family share, so the "
        "part of the payment above the charge goes to the provider."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    adds = ["vt_ccfap_family_benefit"]
