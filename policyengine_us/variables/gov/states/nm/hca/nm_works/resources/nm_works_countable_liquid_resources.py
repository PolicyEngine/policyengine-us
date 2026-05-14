from policyengine_us.model_api import *


class nm_works_countable_liquid_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works countable liquid resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0510.html",
        "https://www.hca.nm.gov/wp-content/uploads/TANF-Final-State-Plan-2024-to-2026.pdf#page=20",
    )
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_cash_assets", period.this_year)
