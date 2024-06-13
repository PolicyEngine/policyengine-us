from policyengine_us.model_api import *


class PellGrantCalculationMethod(Enum):
    EFC = "efc"
    SAI = "sai"


class pell_grant_calculation_method(Variable):
    value_type = Enum
    possible_values = PellGrantCalculationMethod
    default_value = PellGrantCalculationMethod.SAI
    entity = TaxUnit
    definition_period = YEAR
    label = "Pell Grant calculation method"

    def formula(tax_unit, period, parameters):
        tax_units = tax_unit("tax_unit_id", period)
        return np.full_like(
            tax_units,
            PellGrantCalculationMethod.EFC,
            dtype=PellGrantCalculationMethod,
        )

    def formula_2024(tax_unit, period, parameters):
        tax_units = tax_unit("tax_unit_id", period)
        return np.full_like(
            tax_units,
            PellGrantCalculationMethod.SAI,
            dtype=PellGrantCalculationMethod,
        )
