from policyengine_us.model_api import *


class TaxpayerIDType(Enum):
    VALID_SSN = "Valid SSN"
    OTHER_TIN = "Other TIN"
    NONE = "None"


class taxpayer_id_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = TaxpayerIDType
    default_value = TaxpayerIDType.VALID_SSN
    definition_period = YEAR
    label = "Taxpayer ID type for federal tax identification rules"

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values

        derived = np.full(person.count, TaxpayerIDType.OTHER_TIN.name, dtype=object)
        derived[
            (ssn_card_type == ssn_card_types.CITIZEN)
            | (ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD)
        ] = TaxpayerIDType.VALID_SSN.name
        derived[ssn_card_type == ssn_card_types.NONE] = TaxpayerIDType.NONE.name
        return TaxpayerIDType.encode(derived)
