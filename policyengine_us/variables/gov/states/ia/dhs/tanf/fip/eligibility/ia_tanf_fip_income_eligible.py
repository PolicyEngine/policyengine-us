from policyengine_us.model_api import *


class ia_tanf_fip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP income eligible"
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.27 and 441-41.28"
    documentation = (
        "Families are income eligible if they pass both the Standard of "
        "Need test and the Payment Standard test."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Must pass both tests to be income eligible
        passes_standard_of_need = spm_unit(
            "ia_tanf_fip_standard_of_need_test", period
        )
        passes_payment_standard = spm_unit(
            "ia_tanf_fip_payment_standard_test", period
        )

        return passes_standard_of_need & passes_payment_standard
