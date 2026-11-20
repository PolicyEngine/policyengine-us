from policyengine_us.model_api import *


class il_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois LIHEAP base payment"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://liheapch.acf.gov/docs/2024/benefits-matricies/IL_BenefitMatrix_2024.pdf",
        # PDF pages 1-2
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IL_BenefitMatrix_Heat-Cool_2026.pdf#page=1",
        # PDF pages 1-2
        "https://ilvalley-edc.org/wp-content/uploads/2026/06/2027-LIHEAP-Benefit-Matrix-FINAL-20260616.pdf#page=1",
        "https://www.icc.illinois.gov/consumers/utility-energy-assistance",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dceo.liheap.payment.matrix
        fuel_type = spm_unit("il_liheap_heating_type", period)
        # The floor keeps units outside Illinois (bracket 0) on a valid matrix key.
        income_bracket = clip(spm_unit("il_liheap_income_bracket", period), 1, 4)
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
        if parameters(
            period
        ).gov.states.il.dceo.liheap.payment.provider_matrix_in_effect:
            electric_provider = spm_unit("il_liheap_electricity_provider", period)
            gas_provider = spm_unit("il_liheap_natural_gas_provider", period)
            comed = electric_provider == electric_provider.possible_values.COMED
            providers = gas_provider.possible_values
            gas_lid = (
                (gas_provider == providers.AMEREN_ILLINOIS)
                | (gas_provider == providers.NICOR_GAS)
                | (gas_provider == providers.NORTH_SHORE_GAS)
                | (gas_provider == providers.PEOPLES_GAS)
            )
            # LIHEAP customers at these gas utilities qualify automatically for
            # LID. The matrix presumes that coordinated application/enrollment.
            # An unspecified company retains the pre-provider non-LID estimate.
            electric_group = where(comed, "comed", "other")
            matrix_amount = select(
                [
                    comed & is_electric,
                    gas_lid & is_gas,
                    comed & is_gas,
                    comed & is_propane,
                ],
                [
                    p.all_electric_comed[income_bracket][capped_size],
                    p.nat_gas_lid[electric_group][income_bracket][capped_size],
                    p.nat_gas_comed[income_bracket][capped_size],
                    p.propane_comed[income_bracket][capped_size],
                ],
                default=matrix_amount,
            )
        # Cap non-cash benefits at actual heating expenses.
        # Cash (heat in rent) is a direct payment — no expense cap.
        # Deprecated adapter: households without a canonical heating_type
        # keep IL's pre-canonical arbitration exactly (person-level total,
        # else heating_cooling_expense).
        canonical_type = spm_unit("heating_type", period)
        unspecified = canonical_type == canonical_type.possible_values.UNSPECIFIED
        heating_person = add(spm_unit, period, ["heating_expense_person"])
        heating_cooling = spm_unit("heating_cooling_expense", period)
        legacy_expense = where(heating_person > 0, heating_person, heating_cooling)
        heating_expenses = where(
            unspecified, legacy_expense, spm_unit("heating_expense", period)
        )
        return where(
            is_cash,
            matrix_amount,
            min_(matrix_amount, heating_expenses),
        )
