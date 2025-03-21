from policyengine_us.model_api import *


class ma_tafdc_dependent_criteria_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible based on the dependent criteria for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-210"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        dependent_child_present = (
            add(spm_unit, period, ["ma_tafdc_eligible_dependent"]) > 0
        )
        dependent_child_pregnancy_eligible = spm_unit.any(
            spm_unit.members("ma_tafdc_pregnancy_eligible", period)
        )  # adult pregnancy included
        return dependent_child_present | dependent_child_pregnancy_eligible
