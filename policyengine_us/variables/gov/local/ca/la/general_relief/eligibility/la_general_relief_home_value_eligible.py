from policyengine_us.model_api import *


class la_general_relief_home_value_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County General Relief based on the home value requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        home_value = add(spm_unit, period, ["assessed_property_value"])
        p = parameters(period).gov.local.ca.la.general_relief.eligibility.limit
        return home_value <= p.home_value
