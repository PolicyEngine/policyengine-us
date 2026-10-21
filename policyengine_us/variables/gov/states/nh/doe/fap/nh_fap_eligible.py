from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nh_fap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for New Hampshire FAP"
    reference = (
        # PDF pages 10-12,17-18,21,34-36,57,74,76-77.
        "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=10",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap
        size = spm_unit("nh_fap_household_size", period)
        income = spm_unit("nh_fap_countable_income", period)
        limit = spm_unit("nh_fap_income_limit", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor_rate = parameters(period).gov.hhs.liheap.fpg_floor
        # Federal law protects income strictly below this floor when SMI is lower.
        federal_floor = np.round(guideline * floor_rate, 2)
        income_eligible = (income <= limit) | (income < federal_floor)
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
            & income_eligible
            & housing_eligible
            & heating_eligible
            & (heating_type != fuel.NONE)
        )
