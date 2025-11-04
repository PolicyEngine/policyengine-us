from policyengine_us.model_api import *


class pa_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF resource eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter178/chap178toc.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf

        # Get household assets (stock variable - use this_year)
        household_assets = spm_unit("spm_unit_assets", period.this_year)

        # Check if assets are below the resource limit
        resource_limit = p.resource_limit
        return household_assets <= resource_limit
