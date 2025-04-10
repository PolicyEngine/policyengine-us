from policyengine_us.model_api import *


class ILAABDAREA(Enum):
    AREA_1 = "Area 1"
    AREA_2 = "Area 2"
    AREA_3 = "Area 3"
    AREA_4 = "Area 4"
    AREA_5 = "Area 5"
    AREA_6 = "Area 6"
    AREA_7 = "Area 7"
    AREA_8 = "Area 8"


class il_aabd_area(Variable):
    value_type = Enum
    entity = Household
    possible_values = ILAABDAREA
    default_value = ILAABDAREA.AREA_1
    definition_period = MONTH
    defined_for = StateCode.IL
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) area"
    reference = "https://www.dhs.state.il.us/page.aspx?item=12668"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).gov.states.il.dhs.aabd.payment.area
        area_1 = np.isin(county, p.area_1)
        area_2 = np.isin(county, p.area_2)
        area_3 = np.isin(county, p.area_3)
        area_4 = np.isin(county, p.area_4)
        area_5 = np.isin(county, p.area_5)
        area_6 = np.isin(county, p.area_6)
        area_7 = np.isin(county, p.area_7)
        area_8 = np.isin(county, p.area_8)

        conditions = [
            area_1,
            area_2,
            area_3,
            area_4,
            area_5,
            area_6,
            area_7,
            area_8,
        ]
        results = [
            ILAABDAREA.area_1,
            ILAABDAREA.area_2,
            ILAABDAREA.area_3,
            ILAABDAREA.area_4,
            ILAABDAREA.area_5,
            ILAABDAREA.area_6,
            ILAABDAREA.area_7,
            ILAABDAREA.area_8,
        ]

        return select(
            conditions,
            results,
            default=ILAABDAREA.AREA_1,
        )
