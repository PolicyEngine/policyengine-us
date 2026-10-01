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
        # The "at least one qualified member" gate is a modeling assumption with
        # no Kentucky source. 921 KAR 4:116 Section 2(1)(d) requires a Social
        # Security number or permanent residency card for each household member,
        # and Section 2(2) treats the application as incomplete until that is
        # received; neither says whether a mixed-status household is denied,
        # served in full, or served without that member. Section 1(10) defines
        # the energy-purchasing household with no immigration carve-out, so all
        # SPM members count for size and income. Documentation and enrollment
        # windows are unmodeled. No categorical or resource test applies.
        return income_eligible & responsible & has_eligible_member
