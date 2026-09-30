from policyengine_us.model_api import *


class KSLIEAPFuelCategory(Enum):
    NATURAL_GAS = "Natural gas"
    ELECTRICITY = "Electricity"
    PROPANE = "Propane"
    OTHER = "Other"


class ks_liheap_fuel_category(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = KSLIEAPFuelCategory
    default_value = KSLIEAPFuelCategory.OTHER
    definition_period = YEAR
    label = "Kansas LIEAP primary heating fuel category"
    documentation = "Benefit matrix fuel table derived from the canonical heating_type input: natural gas; electricity (including solar); propane; and other for fuel oil, kerosene, wood, coal, other fuels, no heating and an unspecified fuel."
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf#page=4",
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13400.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13400.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        natural_gas = heating_type == types.NATURAL_GAS
        electricity = (heating_type == types.ELECTRICITY) | (
            heating_type == types.SOLAR
        )
        propane = heating_type == types.PROPANE
        other = ~(natural_gas | electricity | propane)
        return select(
            [natural_gas, electricity, propane, other],
            [
                KSLIEAPFuelCategory.NATURAL_GAS,
                KSLIEAPFuelCategory.ELECTRICITY,
                KSLIEAPFuelCategory.PROPANE,
                KSLIEAPFuelCategory.OTHER,
            ],
            default=KSLIEAPFuelCategory.OTHER,
        )
