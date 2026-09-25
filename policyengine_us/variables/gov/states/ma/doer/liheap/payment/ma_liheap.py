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
        # Deprecated adapter: households without a canonical heating_type
        # keep MA's pre-canonical arbitration exactly (person-level total,
        # else the per-fuel bill matching the MA heating type — including
        # the post-subsidy electricity_expense — else
        # heating_cooling_expense). electricity_expense equals
        # pre_subsidy_electricity_expense outside California today (the
        # subsidy list is CA-only), so the canonical path differs from this
        # one only in its dependency graph, not in value.
        canonical_type = spm_unit("heating_type", period)
        unspecified = canonical_type == canonical_type.possible_values.UNSPECIFIED
        heating_person = add(spm_unit, period, ["heating_expense_person"])
        heating_type = spm_unit("ma_liheap_heating_type", period)
        types = heating_type.possible_values
        legacy_fuel_expense = select(
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
        legacy_expense = where(heating_person > 0, heating_person, legacy_fuel_expense)
        actual_expense_amount = where(
            unspecified, legacy_expense, spm_unit("heating_expense", period)
        )
        return where(
            heat_in_rent,
            payment_amount,
            min_(actual_expense_amount, payment_amount),
        )
