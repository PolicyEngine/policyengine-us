from policyengine_us.model_api import *


class or_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF resources eligible"
    definition_period = MONTH
    reference = (
        "https://secure.sos.state.or.us/oard/viewSingleRule.action?ruleVrsnRsn=316195",
        "https://oregon.public.law/rules/oar_461-160-0015",
    )
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf.resources.limit
        # spm_unit_assets is a YEAR variable, access with period.this_year
        countable_resources = spm_unit("spm_unit_assets", period.this_year)
        return countable_resources <= p.amount
