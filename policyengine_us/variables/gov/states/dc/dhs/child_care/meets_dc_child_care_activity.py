from policyengine_us.model_api import *


class meets_dc_child_care_activity(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets DC Childcare Subsidy activity requirements"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Check if an adult in the household meets activity requirements
        is_adult = ~person("is_child", period)

        # Working activity
        working = person("employment_status", period) == 1  # Employed

        # Education/training activity
        in_education = person("in_college", period)
        # Note: Ideally we would have more detailed training/education variables

        # Job search activity - this is a simplification since we don't have a job search variable
        # In a real implementation, this would check for recent job search activities
        seeking_employment = (
            person("employment_status", period) == 3
        )  # Unemployed, seeking work

        # Check if any adult meets any of the activity requirements
        meets_activity = working | in_education | seeking_employment

        # At least one adult in the household must meet activity requirements
        eligible_adult = is_adult & meets_activity

        return spm_unit.any(eligible_adult)
