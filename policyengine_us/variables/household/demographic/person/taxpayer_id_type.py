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
        has_valid_ssn = person("has_valid_ssn", period)

        simulation = person.simulation
        tin_holder = simulation.get_holder("has_tin")
        if period in tin_holder.get_known_periods():
            has_tin = tin_holder.get_array(period)
        else:
            legacy_holder = simulation.get_holder("has_itin")
            if period in legacy_holder.get_known_periods():
                has_tin = legacy_holder.get_array(period)
            else:
                has_tin = has_valid_ssn

        derived = np.full(person.count, TaxpayerIDType.NONE.name, dtype=object)
        derived[has_tin] = TaxpayerIDType.OTHER_TIN.name
        derived[has_valid_ssn] = TaxpayerIDType.VALID_SSN.name
        return TaxpayerIDType.encode(derived)
