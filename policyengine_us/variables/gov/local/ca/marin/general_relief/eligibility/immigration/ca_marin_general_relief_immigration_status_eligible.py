from policyengine_us.model_api import *


class ca_marin_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Marin County General Relief based on the immigration status requirements"
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=10"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_person = person(
            "ca_marin_general_relief_immigration_status_eligible_person", period
        )
        # At least one applicant must meet the immigration eligibility criteria.
        return spm_unit.any(eligible_person)
