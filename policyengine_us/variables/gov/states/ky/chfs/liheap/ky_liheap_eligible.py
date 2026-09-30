from policyengine_us.model_api import *


class ky_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kentucky LIHEAP regular heating eligibility"
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/004/116/"

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ky_liheap_income_eligible", period)
        responsible = (spm_unit("heating_expense", period) > 0) | spm_unit(
            "heat_expense_included_in_rent", period
        )
        has_eligible_member = spm_unit.any(
            spm_unit.members("is_citizen_or_legal_immigrant", period)
        )
        # 921 KAR 4:116 Section 1(10) defines the energy-purchasing household;
        # it does not establish the treatment of ineligible immigrants. Counting
        # all SPM members for size while requiring one qualified member is a
        # provisional assumption, not a verified Kentucky mixed-status rule.
        # Confirm household-size and income adjustments with the operational
        # manual before treating this pathway as supported. Documentation and
        # enrollment windows are unmodeled. No categorical or resource test applies.
        return income_eligible & responsible & has_eligible_member
