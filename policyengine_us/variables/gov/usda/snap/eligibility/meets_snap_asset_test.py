from policyengine_us.model_api import *


class meets_snap_asset_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP asset test"
    documentation = (
        "Whether the SPM unit's financial resources are within SNAP's allowable limit"
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#g",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c",
    )

    def formula(spm_unit, period, parameters):
        # Ineligible members' resources continue to count in their
        # entirety (7 CFR 273.11(c)(1)(i), (c)(2)(i), (c)(3)), but the
        # members themselves are excluded when comparing resources with
        # the resource limits (273.11(c)(1)(ii)(D), (c)(2)(iv)(D)), so an
        # excluded elderly or disabled member does not confer the higher
        # limit. Nonhousehold members' (ineligible students') resources
        # are not considered available to the household (273.11(d)), but
        # assets are modeled at the unit level, so we do not carve out
        # their share at the moment.
        has_elderly_or_disabled = spm_unit(
            "has_snap_elderly_disabled_member", period.first_month
        )
        asset_test = parameters(period).gov.usda.snap.asset_test
        assets = spm_unit("snap_assets", period)
        asset_limit = where(
            has_elderly_or_disabled,
            asset_test.limit.elderly_disabled,
            asset_test.limit.standard,
        )
        return assets <= asset_limit
