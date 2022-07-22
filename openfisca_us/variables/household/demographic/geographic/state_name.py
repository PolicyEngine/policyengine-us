from openfisca_us.model_api import *


class StateName(Enum):
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


class state_name(Variable):
    value_type = Enum
    possible_values = StateName
    default_value = StateName.CA
    entity = Household
    label = "State"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        fips = household("fips", period)
        return (
            pd.Series(fips)
            .map(
                {
                    1: StateName.AL,
                    2: StateName.AK,
                    4: StateName.AZ,
                    5: StateName.AR,
                    6: StateName.CA,
                    8: StateName.CO,
                    9: StateName.CT,
                    10: StateName.DE,
                    11: StateName.DC,
                    12: StateName.FL,
                    13: StateName.GA,
                    15: StateName.HI,
                    16: StateName.ID,
                    17: StateName.IL,
                    18: StateName.IN,
                    19: StateName.IA,
                    20: StateName.KS,
                    21: StateName.KY,
                    22: StateName.LA,
                    23: StateName.ME,
                    24: StateName.MD,
                    25: StateName.MA,
                    26: StateName.MI,
                    27: StateName.MN,
                    28: StateName.MS,
                    29: StateName.MO,
                    30: StateName.MT,
                    31: StateName.NE,
                    32: StateName.NV,
                    33: StateName.NH,
                    34: StateName.NJ,
                    35: StateName.NM,
                    36: StateName.NY,
                    37: StateName.NC,
                    38: StateName.ND,
                    39: StateName.OH,
                    40: StateName.OK,
                    41: StateName.OR,
                    42: StateName.PA,
                    44: StateName.RI,
                    45: StateName.SC,
                    46: StateName.SD,
                    47: StateName.TN,
                    48: StateName.TX,
                    49: StateName.UT,
                    50: StateName.VT,
                    51: StateName.VA,
                    53: StateName.WA,
                    54: StateName.WV,
                    55: StateName.WI,
                    56: StateName.WY,
                    72: StateName.PR,
                }
            )
            .values
        )
