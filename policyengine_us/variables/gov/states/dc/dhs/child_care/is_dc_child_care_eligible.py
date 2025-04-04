from policyengine_us.model_api import *


class is_dc_child_care_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the DC Childcare Subsidy"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        # Check citizenship requirements
        citizenship_eligible = spm_unit(
            "meets_dc_child_care_citizenship", period
        )

        # Check activity requirements, unless waived
        activity_requirement_waived = spm_unit(
            "dc_child_care_activity_requirement_waived", period
        )
        meets_activity = spm_unit("meets_dc_child_care_activity", period)
        activity_eligible = activity_requirement_waived | meets_activity

        # Check income limits, unless waived
        income_requirement_waived = spm_unit(
            "dc_child_care_income_requirement_waived", period
        )
        meets_income = spm_unit("meets_dc_child_care_income_limit", period)
        income_eligible = income_requirement_waived | meets_income

        # Check if in special category that provides automatic eligibility
        special_category = spm_unit(
            "meets_dc_child_care_special_category", period
        )

        # Determine final eligibility
        return (
            citizenship_eligible & activity_eligible & income_eligible
        ) | special_category
