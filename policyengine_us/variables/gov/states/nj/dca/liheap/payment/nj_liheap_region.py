from policyengine_us.model_api import *


class nj_liheap_region(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP payment region"
    defined_for = StateCode.NJ
    reference = ("https://nj.gov/dca/dhcr/offices/docs/FY2026%20Benefit%20Matrix.pdf",)
    documentation = (
        "Region 2 is Warren/Sussex; region 1 is the other nineteen counties. Zero "
        "means a county is unknown or outside New Jersey."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.payment.regions
        county = spm_unit.household("county_str", period)
        return select(
            [np.isin(county, p.region_1), np.isin(county, p.region_2)],
            [1, 2],
            default=0,
        )
