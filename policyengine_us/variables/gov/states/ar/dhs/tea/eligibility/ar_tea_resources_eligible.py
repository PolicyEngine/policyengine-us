from policyengine_us.model_api import *


class ar_tea_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arkansas TEA resources eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 3.4
        p = parameters(period).gov.states.ar.dhs.tea.resources
        # Use federal asset calculation for SPM unit
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
