from policyengine_us.model_api import *


class ga_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia TANF due to resources"
    definition_period = MONTH
    reference = (
        "https://rules.sos.ga.gov/gac/290-2-28-.13",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.resources
        countable_resources = spm_unit("ga_tanf_countable_resources", period)
        return countable_resources <= p.limit
