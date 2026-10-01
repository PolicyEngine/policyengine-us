from policyengine_us.model_api import *


class or_liheap_region(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP payment region"
    defined_for = StateCode.OR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=78,80"
    documentation = "Zero denotes an unknown or out-of-state county; a county is required to select the published schedule."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.payment.regions
        county = spm_unit.household("county_str", period)
        return select(
            [np.isin(county, p.region_1), np.isin(county, p.region_2)],
            [1, 2],
            default=0,
        )
