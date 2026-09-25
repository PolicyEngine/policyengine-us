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

        # Heat-in-rent is a direct subsidy — no expense cap.
        matrix_amount = select(
            [
                heating_type == types.ELECTRICITY,
                heating_type == types.GAS,
                heating_type == types.HEAT_IN_RENT,
                heating_type == types.OIL,
            ],
            [
                p.electricity[housing_type][income_level][capped_size],
                p.gas[housing_type][income_level][capped_size],
                p.heat_in_rent,
                p.oil,
            ],
            default=0,
        )
        heat_in_rent = heating_type == types.HEAT_IN_RENT
        return where(heat_in_rent, matrix_amount, min_(matrix_amount, heating_expenses))
