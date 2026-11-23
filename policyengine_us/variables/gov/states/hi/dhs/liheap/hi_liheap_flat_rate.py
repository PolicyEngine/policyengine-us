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
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.liheap
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # Assume a SOLAR heating type is a net-consuming photovoltaic household,
        # which receives the flat amount.
        heating_type = spm_unit("heating_type", period)
        photovoltaic = heating_type == heating_type.possible_values.SOLAR
        flat_rate = subsidized | photovoltaic
        if p.payment.no_housing_cost_flat_rate_in_effect:
            # Assume a home owned outright is a household with no rent or
            # mortgage expense. A rent-free household has no input. Such a home
            # stays on points when every member is elderly or disabled and all
            # income is fixed.
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
            points_exception = spm_unit.all(elderly | disabled) & fixed_income_only
            flat_rate = flat_rate | (owned_outright & ~points_exception)
        return flat_rate
