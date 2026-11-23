from policyengine_us.model_api import *


class hi_liheap_flat_rate(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Receives the Hawaii LIHEAP flat benefit in place of points"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=2",
        # Draft FY2026 manual 6.1 and 6.2.
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=69",
        # FY2027 plan 2.5 and 3.5. PDF pages 10, 13
        "https://liheapch.acf.gov/docs/2027/state-plans/HI_Plan_2027.pdf#page=10",
        # 2026 application, question 22, shelter expenses.
        "https://humanservices.hawaii.gov/bessd/files/2026/06/2026-Application-Packet.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.liheap
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        pv_status = spm_unit("hi_liheap_photovoltaic_status", period)
        net_consuming_pv = pv_status == pv_status.possible_values.PV_WITH_NET_USAGE
        flat_rate = subsidized | net_consuming_pv
        if p.payment.no_housing_cost_flat_rate_in_effect:
            # A household reporting no rent and no mortgage payment has no rent
            # or mortgage expense. Callers must send one of them for a
            # household that pays.
            no_housing_cost = (add(spm_unit, period, ["rent"]) <= 0) & (
                spm_unit("mortgage_payments", period) <= 0
            )
            # A home paid in full stays on points when every member is elderly
            # or disabled and all income is fixed.
            tenure = spm_unit.household("tenure_type", period)
            owned_outright = tenure == tenure.possible_values.OWNED_OUTRIGHT
            person = spm_unit.members
            elderly = (
                person("age", period) >= p.payment.points.vulnerability.elderly_min_age
            )
            disabled = person("hi_liheap_disabled_member", period)
            other_income = 0
            for source in p.income.sources:
                if source not in p.payment.fixed_income_sources:
                    other_income = other_income + max_(add(person, period, [source]), 0)
            fixed_income_only = (
                spm_unit.sum(other_income) + spm_unit("tanf", period)
            ) == 0
            points_exception = (
                owned_outright & spm_unit.all(elderly | disabled) & fixed_income_only
            )
            flat_rate = flat_rate | (no_housing_cost & ~points_exception)
        return flat_rate
