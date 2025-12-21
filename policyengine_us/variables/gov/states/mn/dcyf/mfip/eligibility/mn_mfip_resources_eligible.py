from policyengine_us.model_api import *


class mn_mfip_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP due to resources"
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.02#stat.256P.02.2"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 256P.02, Subd. 2:
        # Assets must not exceed $10,000.
        p = parameters(period).gov.states.mn.dcyf.mfip.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
