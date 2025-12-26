from policyengine_us.model_api import *


class ks_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Kansas TANF resource eligibility"
    definition_period = MONTH
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/current/keesm5110.htm",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm5000.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per KEESM 5110: Resource limit is $3,000
        p = parameters(period).gov.states.ks.dcf.tanf.resource_limit
        resources = spm_unit("spm_unit_cash_assets", period.this_year)
        return resources <= p.amount
