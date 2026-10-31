from policyengine_us.model_api import *


class vt_liheap_heating_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Vermont LIHEAP standard heating cost"
    defined_for = StateCode.VT
    reference = (
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2916.pdf#page=1",
        # PDF pages 2-3
        "https://humanservices.vermont.gov/sites/ahsnew/files/documents/2026-2027%20Benefits%20Matrx.pdf#page=2",
        # PDF pages 6, 39, 43
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.liheap.payment
        dwelling_type = spm_unit("vt_liheap_dwelling_type", period)
        # A unit with no bedrooms uses the 1-bedroom column.
        bedrooms = clip(spm_unit.household("bedrooms", period), 1, p.max_bedrooms)
        cost = p.heating_cost[dwelling_type]
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        # Rule 2901(a)(14) defines the primary heating fuel as the energy type
        # listed in the standard heating cost tables that provides the largest
        # portion of heat. For a grid-tied solar home with electric heat, as
        # heating_expense assumes, that listed type is electricity, so SOLAR
        # reads the electricity row; an off-grid solar-only home, which has no
        # listed fuel, cannot be distinguished. OTHER and NONE have no row
        # (rule 2916(b)), and UNSPECIFIED is not priced because heating_type is
        # a required input.
        return select(
            [
                fuel == fuels.NATURAL_GAS,
                fuel == fuels.PROPANE,
                fuel == fuels.FUEL_OIL,
                fuel == fuels.KEROSENE,
                (fuel == fuels.ELECTRICITY) | (fuel == fuels.SOLAR),
                (fuel == fuels.WOOD) | (fuel == fuels.COAL),
            ],
            [
                cost.natural_gas[bedrooms],
                cost.propane[bedrooms],
                cost.oil[bedrooms],
                cost.kerosene[bedrooms],
                cost.electricity[bedrooms],
                cost.wood_and_coal[bedrooms],
            ],
            default=0,
        )
