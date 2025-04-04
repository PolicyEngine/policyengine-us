from policyengine_us.model_api import *


class meets_dc_child_care_special_category(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets DC Childcare Subsidy special eligibility category"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.child_care.special_categories

        # Check automatic eligibility conditions

        # TANF recipients
        receives_tanf = spm_unit("tanf", period) > 0
        tanf_eligible = receives_tanf & p.automatic_eligibility.tanf

        # SNAP E&T participants - simplified as we don't have a direct variable
        # In a real implementation, we would check SNAP E&T participation
        snap_et_participant = False  # Placeholder
        snap_eligible = (
            snap_et_participant & p.automatic_eligibility.snap_employment
        )

        # Families below 150% FPL
        fpg = spm_unit("tax_unit_fpg", period)
        income = spm_unit("spm_unit_income", period)
        below_150_fpl = income <= (fpg * 1.5)
        low_income_eligible = below_150_fpl

        return tanf_eligible | snap_eligible | low_income_eligible
