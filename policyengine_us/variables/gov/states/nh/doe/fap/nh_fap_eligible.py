from policyengine_us.model_api import *


class nh_fap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for New Hampshire FAP"
    # PY2027 manual, pages 10-12, 17-18, 21, 34-36, 57, 74, 76-77.
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=21"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        size = spm_unit("nh_fap_household_size", period)
        income = spm_unit("nh_fap_countable_income", period)
        limit = spm_unit("nh_fap_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        heating_cost = spm_unit("nh_fap_heating_cost", period)
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # Subsidized heat-in-rent is excluded. Nonsubsidized heat-in-rent can
        # qualify without a separately reported heating bill.
        housing_eligible = ~(heat_in_rent & subsidized)
        heating_eligible = (heating_cost > 0) | heat_in_rent
        return (
            (size > 0)
            & (income <= limit)
            & housing_eligible
            & heating_eligible
            & (heating_type != fuel.NONE)
        )
