from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wa.dcyf.wccc.payment.wa_wccc_region import (
    WAWCCCRegion,
)


class wa_wccc_center_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = WAWCCCRegion
    default_value = WAWCCCRegion.REGION_2
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC center-rate region with county overrides"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200"

    def formula(household, period, parameters):
        county = household("county_str", period)
        base_region = household("wa_wccc_region", period)
        p = parameters(period).gov.states.wa.dcyf.wccc.region
        override_to_region_3 = np.isin(county, p.center_override_to_region_3_counties)
        override_to_region_6 = np.isin(county, p.center_override_to_region_6_counties)
        return select(
            [override_to_region_3, override_to_region_6],
            [WAWCCCRegion.REGION_3, WAWCCCRegion.REGION_6],
            default=base_region,
        )
