from policyengine_us.model_api import *


class nm_works_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works countable resources"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0510.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        liquid_resources = spm_unit("nm_works_countable_liquid_resources", period)
        non_liquid_resources = spm_unit(
            "nm_works_countable_non_liquid_resources", period
        )
        return liquid_resources + non_liquid_resources
