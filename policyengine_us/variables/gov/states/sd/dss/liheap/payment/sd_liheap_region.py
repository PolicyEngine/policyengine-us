from policyengine_us.model_api import *


class sd_liheap_region(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "South Dakota LIEAP heating region"
    defined_for = StateCode.SD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:15:01:35"
    documentation = (
        "Regions 1 to 4 follow ARSD 67:15:01:35. Zero means the county is unknown "
        "or outside South Dakota. A household with no county input takes the first "
        "South Dakota county, Aurora, in region 2."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.payment.regions
        county = spm_unit.household("county_str", period)
        # Former Shannon County is the Oglala Lakota county identifier.
        return select(
            [
                np.isin(county, p.region_1),
                np.isin(county, p.region_2),
                np.isin(county, p.region_3),
                np.isin(county, p.region_4),
            ],
            [1, 2, 3, 4],
            default=0,
        )
