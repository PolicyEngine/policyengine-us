from policyengine_us.model_api import *


class la_general_relief_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Los Angeles County General Relief based on the age requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.la.general_relief.eligibility
        # Based on the fact sheet and questionnaire, assuming that just the head
        # has to be over the age threshold
        age = add(spm_unit, period, ["age_head"])
        # Person has to reach a certain age
        return age >= p.age_threshold
