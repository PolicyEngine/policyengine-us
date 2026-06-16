from policyengine_us.model_api import *


class ca_scc_general_assistance_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Meets property limit for Santa Clara County General Assistance"
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/08Property/Personal_Property.htm"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.scc.general_assistance.personal_property
        personal_property = add(spm_unit, period.this_year, ["personal_property"])
        return personal_property <= p.limit
