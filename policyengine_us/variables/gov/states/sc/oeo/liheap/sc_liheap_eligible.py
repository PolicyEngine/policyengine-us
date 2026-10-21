from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class sc_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for South Carolina LIHEAP regular heating assistance"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # PDF pages 8-9
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8",
        "https://oeo.sc.gov/managedsites/prd/oeo/liheap.html",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period)
        size = spm_unit("sc_liheap_household_size", period)
        income = spm_unit("sc_liheap_countable_income", period)
        limit = spm_unit("sc_liheap_income_limit", period)
        guideline = fpg(
            max_(size, 1),
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.gov.states.sc.oeo.liheap.eligibility.fpg_year_lag,
        )
        federal_floor = np.round(guideline * p.gov.hhs.liheap.fpg_floor, 2)
        fuel = spm_unit("heating_type", period)
        heating_responsibility = spm_unit("has_heating_expense", period) | spm_unit(
            "heat_expense_included_in_rent", period
        )
        return (
            (size > 0)
            & ((income <= limit) | (income < federal_floor))
            & (fuel != fuel.possible_values.NONE)
            & heating_responsibility
        )
