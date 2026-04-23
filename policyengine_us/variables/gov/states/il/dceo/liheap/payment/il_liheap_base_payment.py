from policyengine_us.model_api import *


class il_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois LIHEAP base payment"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://liheapch.acf.gov/docs/2024/benefits-matricies/IL_BenefitMatrix_2024.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dceo.liheap.payment.matrix
        fuel_type = spm_unit("il_liheap_heating_type", period)
        income_bracket = spm_unit("il_liheap_income_bracket", period)
        size = spm_unit("spm_unit_size", period)
        capped_size = clip(size, 1, 6)

        is_electric = fuel_type == fuel_type.possible_values.ALL_ELECTRIC
        is_gas = fuel_type == fuel_type.possible_values.NAT_GAS_OTHER
        is_propane = fuel_type == fuel_type.possible_values.PROPANE_FUEL_OIL
        is_cash = fuel_type == fuel_type.possible_values.CASH

        matrix_amount = select(
            [is_electric, is_gas, is_propane, is_cash],
            [
                p.all_electric[income_bracket][capped_size],
                p.nat_gas[income_bracket][capped_size],
                p.propane[income_bracket][capped_size],
                p.cash[income_bracket][capped_size],
            ],
            default=0,
        )
        # Cap non-cash benefits at actual heating expenses.
        # Cash (heat in rent) is a direct payment — no expense cap.
        heating_expenses = add(spm_unit, period, ["heating_expense_person"])
        return where(
            is_cash,
            matrix_amount,
            min_(matrix_amount, heating_expenses),
        )
