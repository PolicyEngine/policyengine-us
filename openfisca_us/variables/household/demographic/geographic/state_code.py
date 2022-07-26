from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class StateCode(Enum):
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


class state_code(Variable):
    value_type = Enum
    possible_values = StateCode
    default_value = StateCode.CA
    entity = Household
    label = "State code"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        return StateCode.encode(
            household("state_name", period).decode_to_str()
        )
