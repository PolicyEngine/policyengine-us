from policyengine_us.model_api import *


class ia_cca_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Iowa CCA based on resources"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=5"

    def formula(spm_unit, period, parameters):
        # Iowa's $1 million resource limit is far above the federal CCDF
        # asset limit, so we apply Iowa's own limit rather than reusing the
        # federal CCDF asset check (which would impose a much tighter test
        # than Iowa law allows). Resources are a stock, read annually.
        assets = spm_unit("spm_unit_assets", period.this_year)
        asset_limit = parameters(period).gov.states.ia.hhs.cca.eligibility.asset_limit
        return assets <= asset_limit
