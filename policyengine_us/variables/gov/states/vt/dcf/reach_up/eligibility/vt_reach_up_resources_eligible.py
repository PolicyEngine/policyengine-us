from policyengine_us.model_api import *


class vt_reach_up_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Vermont Reach Up resource eligible"
    definition_period = MONTH
    reference = "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/"
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per 33 V.S.A. Section 1103(a)(1): Resource limit of $9,000
        p = parameters(period).gov.states.vt.dcf.reach_up.resources
        # NOTE: Many exclusions exist (vehicles, retirement accounts, etc.)
        # that are not separately tracked in PolicyEngine
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.limit
