from policyengine_us.model_api import *


class residential_clean_energy_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Residential clean energy credit"
    definition_period = YEAR
    documentation = "Residential clean energy tax credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25D"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.residential_clean_energy
        # Get total expenditures except fuel cell.
        expenditures_less_fuel_cell = add(
            tax_unit,
            period,
            [i for i in p.elements if i != "fuel_cell_property_expenditures"],
        )
        # Get qualifying expenditures for fuel cell.
        # These are capped based on the kilowatts.
        fuel_cell_expenditures = tax_unit(
            "fuel_cell_property_expenditures", period
        )
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
