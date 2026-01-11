from policyengine_us.model_api import *


class nm_works_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico Works resources eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0510.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.510.8 NMAC, resources/property limits:
        # - Liquid resources must not exceed $1,500
        # - Non-liquid resources must not exceed $2,000
        # NOTE: Simplified check using total assets since liquid/non-liquid
        # distinction is not currently modeled. Combined limit used.
        p = parameters(period).gov.states.nm.hca.nm_works.resources.limit
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.liquid + p.non_liquid
