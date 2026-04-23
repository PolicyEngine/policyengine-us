from policyengine_us.model_api import *


class pa_ccw_region(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    label = "Pennsylvania CCW MCCA payment region"
    defined_for = StateCode.PA
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=10",
        "https://www.pa.gov/agencies/dhs/resources/early-learning-child-care/elrc/",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.pa.dhs.ccw.region

        return select(
            [np.isin(county, getattr(p, f"region_{r}")) for r in range(2, 20)],
            list(range(2, 20)),
            default=1,
        )
