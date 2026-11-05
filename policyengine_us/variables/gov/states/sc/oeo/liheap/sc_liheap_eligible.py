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
        # PDF pages 526,536-537
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20South%20Carolina%20LIHEAP%20Model%20Plan%20w%20Attachments.pdf#page=526",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap
        size = spm_unit("sc_liheap_household_size", period)
        income = spm_unit("sc_liheap_countable_income", period)
        limit = spm_unit("sc_liheap_income_limit", period)
        guideline = fpg(
            size,
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        federal_floor = np.round(
            guideline * parameters(period).gov.hhs.liheap.fpg_floor, 2
        )
        # OEO asks for an obligation to pay a home energy bill, and the one regular
        # award pays heating or cooling costs, so any counted bill qualifies, including
        # in a home without heating. heating_type is a required input, so an unspecified
        # fuel qualifies only through heat in the rent.
        has_energy_cost = add(spm_unit, period, p.payment.energy_cost_sources) > 0
        fuel = spm_unit("heating_type", period)
        known_fuel = fuel != fuel.possible_values.UNSPECIFIED
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        return (
            (size > 0)
            & ((income <= limit) | (income < federal_floor))
            & ((has_energy_cost & known_fuel) | heat_in_rent)
        )
