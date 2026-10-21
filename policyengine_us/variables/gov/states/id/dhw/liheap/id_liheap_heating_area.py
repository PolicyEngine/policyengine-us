from policyengine_us.model_api import *


class id_liheap_heating_area(Variable):
    value_type = int
    entity = SPMUnit
    label = "Idaho LIHEAP heating area"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = "https://web.archive.org/web/20170124204651id_/http://healthandwelfare.idaho.gov/portals/_rainbow/manuals/liheap/Appendices/a_codes_all.pdf#page=2"

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period)
        p = parameters(period).gov.states.id.dhw.liheap.payment.heating_areas
        # Area codes match the benefit matrix; zero leaves unmatched counties
        # unassigned. The recovered map's continuation is user-approved.
        return select(
            [
                np.isin(county, p.area_1),
                np.isin(county, p.area_2),
                np.isin(county, p.area_3),
            ],
            [1, 2, 3],
            default=0,
        )
