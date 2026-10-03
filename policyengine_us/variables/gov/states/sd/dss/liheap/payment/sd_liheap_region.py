from policyengine_us.model_api import *


class sd_liheap_region(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "South Dakota LIEAP heating region"
    defined_for = StateCode.SD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:15:01:35"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.payment.regions
        county = spm_unit.household("county_str", period)
        # All 66 counties are assigned by rule; historic Shannon is represented
        # by the existing Oglala Lakota county identifier. Unknown/foreign county
        # is an unsupported location (0), never silently region 1.
        # The shared county formula may infer the first county if no geography
        # is supplied; an observed county is needed for a verified regional amount.
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
