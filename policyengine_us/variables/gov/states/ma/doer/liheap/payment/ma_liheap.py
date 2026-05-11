from policyengine_us.model_api import *


class ma_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP payment"
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        payment_amount = add(
            spm_unit,
            period,
            ["ma_liheap_standard_payment", "ma_liheap_hecs_payment"],
        )
        # Heat-in-rent is a direct subsidy — no expense cap.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_person = add(spm_unit, period, ["heating_expense_person"])
        # Legacy fallback: partners may still send the pre-PR-#7986 per-fuel inputs.
        heating_type = spm_unit("ma_liheap_heating_type", period)
        types = heating_type.possible_values
        legacy_expense = select(
            [
                heating_type == types.ELECTRICITY,
                heating_type == types.NATURAL_GAS,
                heating_type == types.HEATING_OIL_AND_PROPANE,
                heating_type == types.KEROSENE,
            ],
            [
                spm_unit("electricity_expense", period),
                spm_unit("gas_expense", period),
                spm_unit("fuel_oil_expense", period),
                spm_unit("fuel_oil_expense", period),
            ],
            default=spm_unit("heating_cooling_expense", period),
        )
        actual_expense_amount = where(
            heating_person > 0, heating_person, legacy_expense
        )
        return where(
            heat_in_rent,
            payment_amount,
            min_(actual_expense_amount, payment_amount),
        )
