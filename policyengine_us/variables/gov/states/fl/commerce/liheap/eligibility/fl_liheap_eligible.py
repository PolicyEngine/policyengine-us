from policyengine_us.model_api import *


class fl_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Florida LIHEAP regular heating eligibility"
    defined_for = StateCode.FL
    # Plan pages 5 and 8; manual pages 4, 23, 41, 43, 47 and 50.
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=5",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("fl_liheap_household_size", period)
        income = spm_unit("fl_liheap_countable_income", period)
        limit = spm_unit("fl_liheap_income_limit", period)
        categorical = spm_unit("fl_liheap_categorically_eligible", period)
        heating_expense = spm_unit("heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # The nonsubsidized rent flag represents a verified landlord heating
        # arrangement. Actual verification and account ownership are absent
        # from existing inputs. In subsidized heat-in-rent housing, a positive
        # heating expense represents the household's verified excess charge.
        # A direct bill or reported obligation is otherwise residual liability.
        responsible = where(
            heat_in_rent,
            ~subsidized | (heating_expense > 0),
            spm_unit("has_heating_expense", period) | (heating_expense > 0),
        )
        heating_type = spm_unit("heating_type", period)
        return (
            (size > 0)
            & ((income <= limit) | categorical)
            & responsible
            & (heating_type != heating_type.possible_values.NONE)
        )
