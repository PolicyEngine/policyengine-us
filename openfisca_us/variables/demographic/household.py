from openfisca_core.model_api import *
from openfisca_us.entities import *
import numpy as np


class household_id(Variable):
    value_type = float
    entity = Household
    label = u"Unique reference for this household"
    definition_period = ETERNITY


class household_weight(Variable):
    value_type = float
    entity = Household
    label = u"Household weight"
    definition_period = YEAR


class person_household_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for the household of this person"
    definition_period = ETERNITY


class is_household_head(Variable):
    value_type = float
    entity = Person
    label = u"Head of household"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Use order of input (first)
        return person.household.members_position == 0


class State(Enum):
    # Source: https://gist.github.com/rogerallen/1583593#gistcomment-3699885
    # 50 states and DC.
    AL = "Alabama"
    AK = "Alaska"
    AZ = "Arizona"
    AR = "Arkansas"
    CA = "California"
    CO = "Colorado"
    CT = "Connecticut"
    DE = "Delaware"
    FL = "Florida"
    GA = "Georgia"
    HI = "Hawaii"
    ID = "Idaho"
    IL = "Illinois"
    IN = "Indiana"
    IA = "Iowa"
    KS = "Kansas"
    KY = "Kentucky"
    LA = "Louisiana"
    ME = "Maine"
    MD = "Maryland"
    MA = "Massachusetts"
    MI = "Michigan"
    MN = "Minnesota"
    MS = "Mississippi"
    MO = "Missouri"
    MT = "Montana"
    NE = "Nebraska"
    NV = "Nevada"
    NH = "New Hampshire"
    NJ = "New Jersey"
    NM = "New Mexico"
    NY = "New York"
    NC = "North Carolina"
    ND = "North Dakota"
    OH = "Ohio"
    OK = "Oklahoma"
    OR = "Oregon"
    PA = "Pennsylvania"
    RI = "Rhode Island"
    SC = "South Carolina"
    SD = "South Dakota"
    TN = "Tennessee"
    TX = "Texas"
    UT = "Utah"
    VT = "Vermont"
    VA = "Virginia"
    WA = "Washington"
    WV = "West Virginia"
    WI = "Wisconsin"
    WY = "Wyoming"
    DC = "District of Columbia"
    # Territories.
    GU = "Guam"
    MP = "Northern Mariana Islands"
    PW = "Palau"
    PR = "Puerto Rico"
    VI = "Virgin Islands"
    AA = "Armed Forces Americas (Except Canada)"
    AE = "Armed Forces Africa/Canada/Europe/Middle East"
    AP = "Armed Forces Pacific"


class state_code(Variable):
    value_type = Enum
    possible_values = State
    default_value = State.CA
    entity = Household
    label = u"State"
    definition_period = ETERNITY


class state_code_str(Variable):
    value_type = str
    entity = Household
    label = "State code (string)"
    documentation = "State code variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household("state_code", period).decode_to_str()


class StateGroup(Enum):
    CONTIGUOUS_US = "Contiguous US"
    AK = "Alaska"
    HI = "Hawaii"
    GU = "Guam"
    PR = "Puerto Rico"
    VI = "Virgin Islands"
    # Omit other territories for now.


class state_group(Variable):
    value_type = Enum
    possible_values = StateGroup
    default_value = StateGroup.CONTIGUOUS_US
    entity = Household
    label = u"State group"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        NON_CONTIGUOUS_STATES = ("AK", "HI", "GU", "PR", "VI")
        state_code = household("state_code", period).decode_to_str()
        return where(
            np.isin(state_code, NON_CONTIGUOUS_STATES),
            StateGroup.encode(state_code).decode(),
            StateGroup.CONTIGUOUS_US,
        )


class state_group_str(Variable):
    value_type = str
    entity = Household
    label = "State group (string)"
    documentation = "State group variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household("state_group", period).decode_to_str()


# Counties in NY state


class County(Enum):
    ALBANY_NY = "Albany, NY"
    ALLEGANY_NY = "Allegany, NY"
    BRONX_NY = "Bronx, NY"
    BROOME_NY = "Broome, NY"
    CATTARAUGUS_NY = "Cattaraugus, NY"
    CAYUGA_NY = "Cayuga, NY"
    CHAUTAUQUA_NY = "Chautauqua, NY"
    CHEMUNG_NY = "Chemung, NY"
    CHENANGO_NY = "Chenango, NY"
    CLINTON_NY = "Clinton, NY"
    COLUMBIA_NY = "Columbia, NY"
    CORTLAND_NY = "Cortland, NY"
    DELAWARE_NY = "Delaware, NY"
    DUTCHESS_NY = "Dutchess, NY"
    ERIE_NY = "Erie, NY"
    ESSEX_NY = "Essex, NY"
    FRANKLIN_NY = "Franklin, NY"
    FULTON_NY = "Fulton, NY"
    GENESEE_NY = "Genesee, NY"
    GREENE_NY = "Greene, NY"
    HAMILTON_NY = "Hamilton, NY"
    HERKIMER_NY = "Herkimer, NY"
    JEFFERSON_NY = "Jefferson, NY"
    KINGS_NY = "Kings, NY"
    LEWIS_NY = "Lewis, NY"
    LIVINGSTON_NY = "Livingston, NY"
    MADISON_NY = "Madison, NY"
    MONROE_NY = "Monroe, NY"
    MONTGOMERY_NY = "Montgomery, NY"
    NASSAU_NY = "Nassau, NY"
    NEW_YORK_NY = "New York, NY"
    NIAGARA_NY = "Niagara, NY"
    ONEIDA_NY = "Oneida, NY"
    ONONDAGA_NY = "Onondaga, NY"
    ONTARIO_NY = "Ontario, NY"
    ORANGE_NY = "Orange, NY"
    ORLEANS_NY = "Orleans, NY"
    OSWEGO_NY = "Oswego, NY"
    OTSEGO_NY = "Otsego, NY"
    PUTNAM_NY = "Putnam, NY"
    QUEENS_NY = "Queens, NY"
    RENSSELAER_NY = "Rensselaer, NY"
    RICHMOND_NY = "Richmond, NY"
    ROCKLAND_NY = "Rockland, NY"
    ST_LAWRENCE_NY = "St. Lawrence, NY"
    SARATOGA_NY = "Saratoga, NY"
    SCHENECTADY_NY = "Schenectady, NY"
    SCHOHARIE_NY = "Schoharie, NY"
    SCHUYLER_NY = "Schuyler, NY"
    SENECA_NY = "Seneca, NY"
    STEUBEN_NY = "Steuben, NY"
    SUFFOLK_NY = "Suffolk, NY"
    SULLIVAN_NY = "Sullivan, NY"
    TIOGA_NY = "Tioga, NY"
    TOMPKINS_NY = "Tompkins, NY"
    ULSTER_NY = "Ulster, NY"
    WARREN_NY = "Warren, NY"
    WASHINGTON_NY = "Washington, NY"
    WAYNE_NY = "Wayne, NY"
    WESTCHESTER_NY = "Westchester, NY"
    WYOMING_NY = "Wyoming, NY"
    YATES_NY = "Yates, NY"


class county(Variable):
    value_type = Enum
    possible_values = County
    default_value = County.NEW_YORK_NY
    entity = Household
    label = u"County"
    definition_period = ETERNITY


class is_homeless(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    documentation = "Whether all members are homeless individuals and are not receiving free shelter throughout the month"
    label = "Is homeless"


class is_on_tribal_land(Variable):
    value_type = bool
    entity = Household
    definition_period = ETERNITY
    label = "Is on tribal land"
    documentation = "Whether the household is on tribal land"
