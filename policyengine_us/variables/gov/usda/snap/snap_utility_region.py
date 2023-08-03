from policyengine_us.model_api import *


class SnapUtilityRegion(Enum):
    AL = "AL"
    AK = "AK"
    AZ = "AZ"
    AR = "AR"
    CA = "CA"
    CO = "CO"
    CT = "CT"
    DE = "DE"
    FL = "FL"
    GA = "GA"
    HI = "HI"
    ID = "ID"
    IL = "IL"
    IN = "IN"
    IA = "IA"
    KS = "KS"
    KY = "KY"
    LA = "LA"
    ME = "ME"
    MD = "MD"
    MA = "MA"
    MI = "MI"
    MN = "MN"
    MS = "MS"
    MO = "MO"
    MT = "MT"
    NE = "NE"
    NV = "NV"
    NH = "NH"
    NJ = "NJ"
    NM = "NM"
    NY = "NY"
    NC = "NC"
    ND = "ND"
    OH = "OH"
    OK = "OK"
    OR = "OR"
    PA = "PA"
    RI = "RI"
    SC = "SC"
    SD = "SD"
    TN = "TN"
    TX = "TX"
    UT = "UT"
    VT = "VT"
    VA = "VA"
    WA = "WA"
    WV = "WV"
    WI = "WI"
    WY = "WY"
    DC = "DC"
    GU = "GU"
    MP = "MP"
    PW = "PW"
    PR = "PR"
    VI = "VI"
    AA = "AA"
    AE = "AE"
    AP = "AP"


class snap_utility_region(Variable):
    value_type = Enum
    possible_values = SnapUtilityRegion
    default_value = SnapUtilityRegion.CA
    entity = Household
    label = "SNAP utility region"
    documentation = "Region deciding the SNAP utility allowances."
    definition_period = YEAR

    def formula(household, period, parameters):
        return household("state_code", period).decode_to_str()
