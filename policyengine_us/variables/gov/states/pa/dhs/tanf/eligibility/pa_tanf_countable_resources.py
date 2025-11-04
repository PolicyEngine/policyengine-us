from policyengine_us.model_api import *


class pa_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183 - Resources"
    documentation = "Total countable resources for Pennsylvania TANF eligibility. Pennsylvania excludes the primary residence and one vehicle per household (regardless of value). https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        # Total household assets
        total_assets = spm_unit("spm_unit_assets", period)

        # Pennsylvania excludes:
        # 1. Primary residence (home)
        # 2. One vehicle per household (regardless of value)
        # For initial implementation, we use total assets
        # Future enhancement: implement specific exclusions

        return total_assets
