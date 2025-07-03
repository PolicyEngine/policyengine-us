from policyengine_us.model_api import *


class dc_liheap_payment(Variable):
    value_type = float
    entity = Household
    label = "Eligible for the DC LIHEAP"
    unit = USD
    definition_period = YEAR
    defined_for = "dc_liheap_eligible"
    reference = "https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DOEE%20FY24%20LIHEAP_REGULAR_Benefits_Table-Matrix.pdf"

    def formula(household, period, parameters):
        p = parameters(period).gov.states.dc.doee.liheap
        housing_type = household("housing_type", period)
        utility_type = household("dc_liheap_utility_type", period)
        income_level = household("dc_liheap_income_level", period)
        size = household("household_size", period)
        capped_size = clip(size, 1, 4)

        electric = utility_type == utility_type.possible_values.ELECTRIC
        uncapped_electric_payment = p.electric[housing_type][income_level][
            capped_size
        ]
        electric_expense = add(
            household, period, ["pre_subsidy_electricity_expense"]
        )
        electric_payment = min_(uncapped_electric_payment, electric_expense)

        gas = utility_type == utility_type.possible_values.GAS
        uncapped_gas_payment = p.gas[housing_type][income_level][capped_size]
        gas_expense = add(household, period, ["gas_expense"])
        gas_payment = min_(uncapped_gas_payment, gas_expense)

        heat_in_rent = (
            utility_type == utility_type.possible_values.HEAT_IN_RENT
        )
        heat_in_rent_payment = p.heat_in_rent

        oil = utility_type == utility_type.possible_values.OIL
        uncapped_oil_payment = p.oil
        oil_expense = add(household, period, ["oil_expense"])
        oil_payment = min_(uncapped_oil_payment, oil_expense)

        return select(
            [electric, gas, heat_in_rent, oil],
            [electric_payment, gas_payment, heat_in_rent_payment, oil_payment],
        )
