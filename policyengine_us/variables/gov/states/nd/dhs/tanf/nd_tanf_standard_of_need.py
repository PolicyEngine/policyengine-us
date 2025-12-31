from policyengine_us.model_api import *


class nd_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF standard of need"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.nd.gov/news/hhs-announces-tanf-modernization-effort-aimed-increasing-accessibility-resources-during",
        "https://nd.gov/dhs/policymanuals/40019/Archive%20Documents/2023%20-%20ML%203749/400_19_110_20.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.benefit.standard_of_need
        # Per TANF modernization (August 2023): Standard of Need is 50% of FPL
        # tanf_fpg already returns monthly FPL for the SPM unit
        monthly_fpg = spm_unit("tanf_fpg", period)
        return monthly_fpg * p.rate
