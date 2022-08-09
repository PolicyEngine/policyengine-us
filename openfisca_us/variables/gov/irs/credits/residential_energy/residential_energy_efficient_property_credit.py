from openfisca_us.model_api import *


class residential_energy_efficient_property_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Residential energy efficient property tax credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25D"

    def formula(tax_unit, period, parameters):
        # Get total expenditures except fuel cell.
        EXPENDITURES_LESS_FUEL_CELL = [
            "biomass_fuel_property_expenditures",
            "geothermal_heat_pump_property_expenditures",
            "small_wind_energy_property_expenditures",
            "solar_electric_property_expenditures",
            "solar_water_heating_property_expenditures",
        ]
        expenditures_less_fuel_cell = add(
            tax_unit, period, EXPENDITURES_LESS_FUEL_CELL
        )
        # Get qualifying expenditures for fuel cell.
        # These are capped based on the kilowatts.
        fuel_cell_expenditures = tax_unit(
            "fuel_cell_property_expenditures", period
        )
        p = parameters(period).gov.irs.credits.residential_energy
        fuel_cell_cap = p.fuel_cell_cap_per_kw * tax_unit(
            "fuel_cell_property_capacity", period
        )
        capped_fuel_cell_expenditures = min_(
            fuel_cell_expenditures, fuel_cell_cap
        )
        qualifying_expenditures = (
            expenditures_less_fuel_cell + capped_fuel_cell_expenditures
        )
        # Flat percentage of qualifying expenditures.
        return qualifying_expenditures * p.applicable_percentage
