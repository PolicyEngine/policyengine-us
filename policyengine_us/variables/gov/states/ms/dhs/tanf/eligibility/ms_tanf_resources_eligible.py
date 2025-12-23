from policyengine_us.model_api import *


class ms_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Mississippi TANF resources eligibility"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
        "https://www.mdhs.ms.gov/help/tanf/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.tanf.resources
        household_assets = spm_unit("spm_unit_assets", period.this_year)
        return household_assets <= p.limit
