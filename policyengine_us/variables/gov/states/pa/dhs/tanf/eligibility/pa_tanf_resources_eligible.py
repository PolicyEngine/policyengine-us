from policyengine_us.model_api import *


class pa_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF resources eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter178/chap178toc.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf

        household_assets = spm_unit("spm_unit_assets", period.this_year)

        return household_assets <= p.resource_limit
