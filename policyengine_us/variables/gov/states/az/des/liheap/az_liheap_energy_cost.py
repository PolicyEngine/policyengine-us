from policyengine_us.model_api import *


class az_liheap_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arizona LIHEAP annual energy cost"
    documentation = "Annual electricity, gas and portable fuel bills entering the energy burden, the worksheet's 'Electric + Gas + Portable Fuel = Total Monthly Cost' taken over the year. Water for evaporative cooling, sewer, trash and phone bills are excluded."
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AZ_BenefitMatrix_Heating_2026.pdf#page=1",
        # Energy Utility and Portable Fuel definitions (pages 4-5).
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=4",
    )
    defined_for = StateCode.AZ

    # "Energy Utility: A service or Portable Fuel that provides a source of
    # heating or cooling for a Household. Eligible Energy Utility service
    # providers include vendors of electricity, gas, or portable fuel" (page 4);
    # "Portable Fuel: Energy that is derived from propane, wood, coal, fuel for
    # gas generators, and/or pellets" (page 5). Fuel oil and other heating fuel
    # bills are purchased home energy and are counted with them. The electric
    # bill is read before subsidies, as heating_expense does, so the burden is
    # gross of discount programs and no subsidy chain feeds back into LIHEAP.
    adds = [
        "pre_subsidy_electricity_expense",
        "gas_expense",
        "bottled_gas_expense",
        "wood_expense",
        "coal_expense",
        "fuel_oil_expense",
        "other_heating_fuel_expense",
    ]
