from policyengine_us.model_api import *


class vt_ccfap_child_payment(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    defined_for = "vt_ccfap_eligible_child"
    label = "Vermont CCFAP payment to the child's provider"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition%20(1).pdf#page=8",
    )

    def formula(person, period, parameters):
        # The state pays each provider the child's rate less the part of the
        # family share assigned to that provider.
        eligible = person.spm_unit("vt_ccfap_eligible", period)
        rate = person("vt_ccfap_child_rate", period)
        share = person("vt_ccfap_assigned_family_share", period)
        return where(eligible, rate - share, 0)
