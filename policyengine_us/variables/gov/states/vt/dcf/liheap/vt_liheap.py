from policyengine_us.model_api import *


class vt_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Vermont LIHEAP regular heating benefit"
    defined_for = "vt_liheap_eligible"
    reference = (
        # PDF pages 39-41
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=39",
        "https://legislature.vermont.gov/statutes/section/33/026/02605",
        # PDF pages 7-9
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2914D.pdf#page=7",
    )
    documentation = (
        "Annual Seasonal Fuel Assistance benefit, verified for the 2025-26 and "
        "2026-27 heating seasons (model years 2026 and 2027); earlier years use "
        "backfilled parameters and are unverified estimates. The payment rate is "
        "an estimate because DCF does not publish it. Applications are assumed "
        "to arrive outside December to February, so the 80%, 60% and 40% "
        "late-application reductions are not applied. Roomer or boarder "
        "households ($21) and excludable members have no inputs, and annual "
        "income stands in for the 30-day lookback."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.liheap.payment
        percentage = spm_unit("vt_liheap_heat_cost_percentage", period)
        heating_cost = spm_unit("vt_liheap_heating_cost", period)
        ratable_benefit = percentage * heating_cost * p.payment_rate
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        heat_in_rent_benefit = max_(
            ratable_benefit * p.heat_in_rent_rate, p.heat_in_rent_minimum
        )
        benefit = select(
            [heat_in_rent & subsidized, heat_in_rent, subsidized],
            [
                p.nominal_benefit,
                heat_in_rent_benefit,
                ratable_benefit * p.subsidized_rate,
            ],
            default=ratable_benefit,
        )
        # Rule 2914(d) rounds the net benefit down to the whole dollar.
        return np.floor(benefit)
