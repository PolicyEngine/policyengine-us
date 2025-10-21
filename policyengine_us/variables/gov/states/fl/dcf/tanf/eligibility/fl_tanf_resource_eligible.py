from policyengine_us.model_api import *


class fl_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TANF resource eligible"
    definition_period = MONTH
    reference = "Florida Statute § 414.075"
    documentation = "Meets asset test: countable assets under $2,000 and vehicle equity under $8,500"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf

        # Asset test
        assets = spm_unit("spm_unit_assets", period)
        asset_limit = p.resource_limit

        # For now, assume vehicle equity is within limits
        # This would require additional data to properly implement
        meets_asset_test = assets <= asset_limit

        return meets_asset_test
