"""
Connecticut TFA resource/asset eligibility.
"""

from policyengine_us.model_api import *


class ct_tfa_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut TFA resource eligibility"
    definition_period = YEAR
    defined_for = StateCode.CT
    documentation = (
        "Connecticut TFA requires total countable assets to be below $6,000. "
        "One vehicle is excluded if total value minus any amount owed is under "
        "$9,500 or if used to transport a household member with a disability. "
        "Home property is not counted toward asset limits."
    )
    reference = (
        "Connecticut TFA Fact Sheet - Asset Limits; "
        "https://portal.ct.gov/dss/knowledge-base/articles/fact-sheets-and-brochures-articles/fact-sheets-articles/tfa-fact-sheet"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.asset_limits

        # Get household assets
        assets = spm_unit("spm_unit_assets", period)

        # Asset limit
        asset_limit = p.general

        # Check if assets are below limit
        return assets <= asset_limit
