from policyengine_us.model_api import *


class ca_smc_general_assistance(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Mateo County General Assistance"
    definition_period = MONTH
    defined_for = "ca_smc_general_assistance_eligible"
    reference = (
        "https://www.smcgov.org/media/153295/download?inline=#page=2",
        "https://www.smcgov.org/media/156974/download?inline=",
    )

    def formula(spm_unit, period, parameters):
        standard = spm_unit("ca_smc_general_assistance_payment_standard", period)
        income = spm_unit("ca_smc_general_assistance_countable_income", period)
        n_eligible = add(
            spm_unit, period, ["ca_smc_general_assistance_eligible_person"]
        )
        per_person_income = where(n_eligible > 0, income / n_eligible, 0)
        per_person_benefit = max_(standard - max_(per_person_income, 0), 0)
        return n_eligible * per_person_benefit
