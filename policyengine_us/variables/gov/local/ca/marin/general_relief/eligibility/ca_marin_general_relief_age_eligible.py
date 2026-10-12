from policyengine_us.model_api import *


class ca_marin_general_relief_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Marin County General Relief based on the age requirements"
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=10"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.marin.general_relief.eligibility
        # The Standards require the applicant to be at least 18 years old. We
        # assume the head of the unit is the applicant. The married/emancipated
        # under-18 exception is not modeled at the moment.
        age = add(spm_unit, period, ["age_head"])
        return age >= p.age_threshold
