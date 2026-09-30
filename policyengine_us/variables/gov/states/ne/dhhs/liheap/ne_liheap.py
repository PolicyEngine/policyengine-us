from policyengine_us.model_api import *


class ne_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP regular heating assistance"
    defined_for = "ne_liheap_eligible"
    reference = "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=2"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap
        gross = spm_unit("ne_liheap_gross_income", period)
        earned = spm_unit("ne_liheap_earned_income", period)
        income = max_(gross - earned * p.earned_income_disregard, 0)
        size = spm_unit("ne_liheap_household_size", period)
        fpg = spm_unit("ne_liheap_fpg", period)
        state_group = spm_unit.household("state_group_str", period)
        fpg_year = period.start.year - int(p.fpg_year_lag)
        federal = parameters(f"{fpg_year}-01-01").gov.hhs.fpg
        # The payment bands stop growing at six people; eligibility does not.
        payment_fpg = fpg - federal.additional_person[state_group] * max_(
            size - p.payment_size_limit, 0
        )
        income_ratio = income / max_(payment_fpg, 1)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        # Single-family schedule only: no existing input distinguishes the
        # 476 NAC 1-004.11/.16 dwelling categories. Multifamily rates are not
        # inferred from tenure or subsidy status. This remains partial coverage.
        # OTHER cannot isolate corn; SOLAR/UNSPECIFIED also lack a supported
        # single-family table mapping. These fuel categories return zero.
        # No FY2026 supplemental heating amount has been verified.
        return select(
            [
                (fuel == types.FUEL_OIL) | (fuel == types.KEROSENE),
                fuel == types.WOOD,
                fuel == types.PROPANE,
                (fuel == types.NATURAL_GAS)
                | (fuel == types.ELECTRICITY)
                | (fuel == types.COAL),
            ],
            [
                p.payment.oil.calc(income_ratio, right=True),
                p.payment.wood.calc(income_ratio, right=True),
                p.payment.propane.calc(income_ratio, right=True),
                p.payment.utility.calc(income_ratio, right=True),
            ],
            default=0,
        )
