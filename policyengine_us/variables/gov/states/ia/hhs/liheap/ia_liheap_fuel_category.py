from policyengine_us.model_api import *


class IALIHEAPFuelCategory(Enum):
    NATURAL_GAS = "Natural gas"
    ELECTRICITY = "Electricity"
    PROPANE = "Liquid propane"
    FUEL_OIL = "Fuel oil"
    SOLID_FUEL = "Solid fuel (wood, coal or corn)"
    OTHER = "Other"


class ia_liheap_fuel_category(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = IALIHEAPFuelCategory
    default_value = IALIHEAPFuelCategory.OTHER
    definition_period = YEAR
    label = "Iowa LIHEAP primary heating fuel category"
    documentation = (
        "Payment matrix fuel row derived from the canonical heating_type input: "
        "natural gas; electricity; liquid propane; fuel oil (including "
        "kerosene); solid fuel for wood and coal; and other for every remaining "
        "fuel, solar, no heating and an unspecified fuel, which carry no "
        "published points."
    )
    reference = (
        # Appendix I item 3, Fuel/Energy Type (page 137); Section 12.00 and
        # 12.20 vendor fuel lists (pages 46-47); Definitions, Primary Heating
        # Fuel Type (page 84).
        "https://hhs.iowa.gov/media/17262/download?inline#page=137",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        natural_gas = heating_type == types.NATURAL_GAS
        electricity = heating_type == types.ELECTRICITY
        propane = heating_type == types.PROPANE
        # Appendix I prints points for "Fuel Oil" but none for kerosene.
        # Section 12.20 groups "LP, heating oil, wood, kerosene, and corn" as
        # deliverable fuels, and heating_expense already pairs kerosene with
        # fuel oil, so kerosene takes the fuel oil points. This is an
        # inference, not an express rule; the flat deliverable fuel benefit in
        # ia_liheap still applies only to liquid propane and fuel oil.
        fuel_oil = (heating_type == types.FUEL_OIL) | (heating_type == types.KEROSENE)
        # Appendix I: "Solid Fuel (Wood/Coal/Corn)". The model has no corn
        # heating type.
        solid_fuel = (heating_type == types.WOOD) | (heating_type == types.COAL)
        return select(
            [natural_gas, electricity, propane, fuel_oil, solid_fuel],
            [
                IALIHEAPFuelCategory.NATURAL_GAS,
                IALIHEAPFuelCategory.ELECTRICITY,
                IALIHEAPFuelCategory.PROPANE,
                IALIHEAPFuelCategory.FUEL_OIL,
                IALIHEAPFuelCategory.SOLID_FUEL,
            ],
            default=IALIHEAPFuelCategory.OTHER,
        )
