from policyengine_us.model_api import *


class ri_liheap_heating_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island LIHEAP heating benefit"
    definition_period = YEAR
    unit = USD
    defined_for = "ri_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.benefit
        heating_type = spm_unit("ri_liheap_heating_type", period)
        fpg_ratio = spm_unit("ri_liheap_fpg_ratio", period)
        is_subsidized = spm_unit("receives_housing_assistance", period)

        # Heating type enum values
        ht = heating_type.possible_values
        is_deliverable = heating_type == ht.DELIVERABLE
        is_natural_gas = heating_type == ht.NATURAL_GAS
        is_electric = heating_type == ht.ELECTRIC
        is_heat_in_rent = heating_type == ht.HEAT_IN_RENT

        # Calculate benefits by fuel type using bracketed parameters
        deliverable_benefit = p.deliverable.amount.calc(fpg_ratio)
        natural_gas_benefit = p.natural_gas.amount.calc(fpg_ratio)
        electric_benefit = p.electric.amount.calc(fpg_ratio)

        # Heat in rent: flat payment plus potential secondary electric
        heat_in_rent_payment = p.heat_in_rent.direct_pay
        secondary_electric = where(
            is_subsidized,
            p.subsidized_housing.secondary_electric,
            p.heat_in_rent.secondary_electric,
        )

        return select(
            [is_deliverable, is_natural_gas, is_electric, is_heat_in_rent],
            [
                deliverable_benefit,
                natural_gas_benefit,
                electric_benefit,
                heat_in_rent_payment + secondary_electric,
            ],
            default=0,
        )
