from policyengine_us.model_api import *


class dc_liheap_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC LIHEAP payment"
    unit = USD
    definition_period = YEAR
    defined_for = "dc_liheap_eligible"
    reference = (
        "https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DOEE%20FY24%20LIHEAP_REGULAR_Benefits_Table-Matrix.pdf",
        "https://doee.dc.gov/liheap",
        "https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DC%20DOEE%20-%20FY26%20LIHEAP%20Benefit%20Matrix.docx",
        "https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/LIHEAP%20FAQ_1_0.pdf#page=1",
        # PDF pages 4, 11
        "https://liheapch.acf.gov/docs/2026/state-plans/DC_Plan_2026.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.doee.liheap.payment
        housing_type = spm_unit("dc_liheap_housing_type", period)
        heating_type = spm_unit("dc_liheap_heating_type", period)
        # The floor keeps units outside DC (income level 0) on a valid matrix key.
        income_level = max_(spm_unit("dc_liheap_income_level", period), 1)
        capped_size = clip(spm_unit("spm_unit_size", period), 1, 4)
        types = heating_type.possible_values

        # Deprecated adapter: households without a canonical heating_type
        # keep DC's pre-canonical expense arbitration (person-level total,
        # else the per-fuel bill matching the DC heating type). One declared
        # change on this path: DC never read heat_expense_included_in_rent
        # before, and dc_liheap_heating_type now selects the heat-in-rent
        # row from it whether or not heating_type is known.
        canonical_type = spm_unit("heating_type", period)
        unspecified = canonical_type == canonical_type.possible_values.UNSPECIFIED
        heating_person = add(spm_unit, period, ["heating_expense_person"])
        legacy_fuel_expense = select(
            [
                heating_type == types.ELECTRICITY,
                heating_type == types.GAS,
                heating_type == types.OIL,
            ],
            [
                spm_unit("pre_subsidy_electricity_expense", period),
                spm_unit("gas_expense", period),
                spm_unit("fuel_oil_expense", period),
            ],
            default=0,
        )
        legacy_expense = where(heating_person > 0, heating_person, legacy_fuel_expense)
        heating_expenses = where(
            unspecified, legacy_expense, spm_unit("heating_expense", period)
        )
        # The one-time Regular benefit helps with heating and cooling costs, with
        # no fuel condition. A household with a known heating type, no heat in
        # the rent and no heating cost that pays for cooling takes the Electric
        # row, capped at its electricity bill, whatever its heating row is.
        heat_in_rent = heating_type == types.HEAT_IN_RENT
        cooling_only = (
            ~unspecified
            & ~heat_in_rent
            & (heating_expenses == 0)
            & spm_unit("has_cooling_expense", period)
        )
        expense_cap = where(
            cooling_only,
            spm_unit("pre_subsidy_electricity_expense", period),
            heating_expenses,
        )

        # Heat-in-rent is a direct subsidy — no expense cap.
        electricity_amount = p.electricity[housing_type][income_level][capped_size]
        heating_amount = select(
            [
                heating_type == types.ELECTRICITY,
                heating_type == types.GAS,
                heating_type == types.HEAT_IN_RENT,
                heating_type == types.OIL,
            ],
            [
                electricity_amount,
                p.gas[housing_type][income_level][capped_size],
                p.heat_in_rent,
                p.oil,
            ],
            default=0,
        )
        matrix_amount = where(cooling_only, electricity_amount, heating_amount)
        return where(heat_in_rent, matrix_amount, min_(matrix_amount, expense_cap))
