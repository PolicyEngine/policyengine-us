from policyengine_us.model_api import *


class la_general_relief_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief based on the personal property value requirements"
    definition_period = YEAR
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        personal_property = add(spm_unit, period, ["personal_property"])
        p = parameters(period).gov.local.ca.la.general_relief.eligibility.limit
        return personal_property < p.personal_property
