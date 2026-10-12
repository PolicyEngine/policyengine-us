from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.income_limits import (
    lookup_sized_income_limit,
)


class hud_low_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD low income limit"
    unit = USD
    documentation = (
        "HUD Section 8 low income limit for the SPM unit's county and family size"
    )
    definition_period = YEAR
    reference = "https://www.huduser.gov/portal/datasets/il.html"

    def formula(spm_unit, period, parameters):
        county_fips = spm_unit.household("county_fips", period)
        size = spm_unit("spm_unit_size", period)
        return lookup_sized_income_limit(
            county_fips,
            size,
            period.start.year,
            "low_income",
        )
