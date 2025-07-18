from policyengine_us.model_api import *


class dc_liheap_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC LIHEAP payment"
    unit = USD
    definition_period = YEAR
    defined_for = "dc_liheap_eligible"
    reference = "https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DOEE%20FY24%20LIHEAP_REGULAR_Benefits_Table-Matrix.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.doee.liheap.payment
        housing_type = spm_unit("dc_liheap_housing_type", period)
        heating_type = spm_unit("dc_liheap_heating_type", period)
        income_level = spm_unit("dc_liheap_income_level", period)
        size = spm_unit("spm_unit_size", period)
        capped_size = clip(size, 1, 4)

        electricity = heating_type == heating_type.possible_values.ELECTRICITY
        uncapped_electricity_payment = p.electricity[housing_type][
            income_level
        ][capped_size]
        electricity_expense = spm_unit(
            "pre_subsidy_electricity_expense", period
        )
        electricity_payment = min_(
            uncapped_electricity_payment, electricity_expense
        )

        gas = heating_type == heating_type.possible_values.GAS
        uncapped_gas_payment = p.gas[housing_type][income_level][capped_size]
        gas_expense = spm_unit("gas_expense", period)
        gas_payment = min_(uncapped_gas_payment, gas_expense)

        heat_in_rent = (
            heating_type == heating_type.possible_values.HEAT_IN_RENT
        )

        oil = heating_type == heating_type.possible_values.OIL
        oil_expense = spm_unit("fuel_oil_expense", period)
        oil_payment = min_(p.oil, oil_expense)

        return select(
            [electricity, gas, heat_in_rent, oil],
            [
                electricity_payment,
                gas_payment,
                p.heat_in_rent,
                oil_payment,
            ],
            default=0,
        )
