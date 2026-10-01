from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ne_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP regular heating assistance"
    documentation = (
        "Verified for FY2026. Earlier years use model parameter backfilling "
        "and are unverified historical estimates."
    )
    defined_for = "ne_liheap_eligible"
    reference = "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap
        gross = spm_unit("ne_liheap_gross_income", period)
        earned = spm_unit("ne_liheap_earned_income", period)
        income = max_(gross - earned * p.earned_income_disregard, 0)
        size = spm_unit("ne_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # The payment bands stop growing at six people; eligibility does not.
        payment_fpg = fpg(
            clip(size, 1, p.payment_size_limit),
            state_group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        payment_fpg = where(size > 0, payment_fpg, 0)
        income_ratio = income / max_(payment_fpg, 1)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        dwelling = spm_unit("ne_liheap_dwelling_type", period)
        multifamily = dwelling == dwelling.possible_values.MULTI_FAMILY
        # Corn shares the natural gas/electricity/coal payment column. No
        # separate schedule is needed, but the fuel enum cannot isolate corn
        # from OTHER. Single-family OTHER/SOLAR/UNSPECIFIED remain unmapped;
        # the multifamily column covers all fuel types.
        # No FY2026 supplemental heating amount has been verified.
        return select(
            [
                multifamily,
                (fuel == types.FUEL_OIL) | (fuel == types.KEROSENE),
                fuel == types.WOOD,
                fuel == types.PROPANE,
                (fuel == types.NATURAL_GAS)
                | (fuel == types.ELECTRICITY)
                | (fuel == types.COAL),
            ],
            [
                p.payment.multifamily.calc(income_ratio, right=True),
                p.payment.oil.calc(income_ratio, right=True),
                p.payment.wood.calc(income_ratio, right=True),
                p.payment.propane.calc(income_ratio, right=True),
                p.payment.utility.calc(income_ratio, right=True),
            ],
            default=0,
        )
