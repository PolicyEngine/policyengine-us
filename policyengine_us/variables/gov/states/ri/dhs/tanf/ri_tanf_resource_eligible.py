from policyengine_us.model_api import *


class ri_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Resource eligible for Rhode Island TANF"
    definition_period = MONTH
    reference = (
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
        "https://dhs.ri.gov/programs-and-services/ri-works-program/eligibility-how-apply",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.tanf
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.resource_limit
