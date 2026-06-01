from policyengine_us.model_api import *


class ca_oc_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Orange County General Relief due to immigration status"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2040%20-%20Approved%20-%20January%202026.pdf#page=01"

    def formula(person, period, parameters):
        # NOTE: Section 40.1 also makes victims of trafficking, domestic
        # violence, and other serious crimes (T/U-visa, VAWA) eligible, but
        # PolicyEngine's ImmigrationStatus enum has no value for that pathway,
        # so we don't track it at the moment.
        p = parameters(period).gov.local.ca.oc.general_relief.eligibility
        status = person("immigration_status", period.this_year).decode_to_str()
        return np.isin(status, p.qualified_immigration_status)
