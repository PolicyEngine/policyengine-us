from policyengine_us.model_api import *


class meets_dc_child_care_citizenship(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets DC Childcare Subsidy citizenship requirements"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Check if there are eligible children based on citizenship
        child_citizenship_eligible = person(
            "dc_child_care_child_citizenship_eligible", period
        )

        # At least one eligible child required
        return spm_unit.any(child_citizenship_eligible)
