from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nm.hca.premium_assistance.puente.nm_puente_health_eligible import (
    nm_puente_health_fpl_ratio,
)


class nm_puente_health_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Puente Health premium assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "nm_puente_health_eligible"
    reference = (
        # Addendum 2, Premium Assistance Parameters and Calculating Monthly
        # Premium Assistance Payments: SLCSP x 1.1 minus a 0% contribution,
        # with a $0 net premium floor (PY2026).
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/3527710a-f9f6-4e8f-9cd7-d9ea1010b653/Addendum%202_%20MAP%20P%26P%20Puente%20Health.pdf#page=3",
        # FINAL PY2027 MAP manual: Table 1 (p.4), the New Mexico Premium
        # Assistance formulas and $0 floor (p.5), and the Puente Health
        # parameters applying them (pp.7-8).
        # PDF pages 4-5, 7-8
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/b61d3073-c0e6-4426-bb40-4cfef26fdca4/FINAL%202027%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=4",
        # 8.401.2.11(D)(1)(a) NMAC: benchmark premium minus the applicable
        # percentage of income, with no federal credit term. The rule in force
        # is one HTML page; HCA's proposed amendment reprints it on PDF page 5.
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/45b8668e-460f-45cd-804f-92ee3d442343/8.401.2.html",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/d3ee1d62-6f0f-4df7-b7fc-96a4c523ea89/08.401.0002_amended.pdf#page=5",
    )
    documentation = (
        "State premium assistance for the tax unit's Puente Health members: "
        "their benchmark premium, increased by 10% below the gross-up limit "
        "of base New Mexico Premium Assistance, minus the Table 1 share of "
        "household income, floored at zero and capped at the premium of the "
        "plan they select (the $0 net premium floor). PY2026 covers income "
        "under 100% of the poverty line, where Table 1's share is 0% and the "
        "10% increase applies, so a member pays nothing for a plan priced up "
        "to 110% of the benchmark. PY2027 applies the Table 1 scale up to "
        "400% and the increase below 200%. The rule's formula has no federal "
        "credit term, since Puente Health members receive none. In a family "
        "with both Puente Health members and members who get the federal "
        "credit, the model subtracts the Table 1 share of the whole "
        "household's income here and again in base New Mexico Premium "
        "Assistance; the sources do not say how BeWell divides it."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance
        # Addendum 2 increases the benchmark by 10% for every PY2026 enrollee
        # (all under 100% of the poverty line); the PY2027 manual applies the
        # base program's increase "under 200% (< 200%)". Both follow from the
        # base program's gross-up limit and boundary on the exact ratio.
        ratio = nm_puente_health_fpl_ratio(tax_unit, period)
        limit = p.benchmark_gross_up.fpl_limit
        gross_up_applies = where(
            p.benchmark_gross_up.boundary_inclusive,
            ratio <= limit,
            ratio < limit,
        )
        gross_up = where(gross_up_applies, 1 + p.benchmark_gross_up.rate, 1)
        benchmark = add(tax_unit, period, ["nm_puente_health_benchmark_premium"])
        # Table 1, which Puente Health enrollees "between 0 and <= 400% of the
        # FPL follow" (PY2027 manual p.8); its 0% share below 150% is the
        # Addendum's 0% contribution under 100% (PY2026).
        target_percentage = tax_unit(
            "nm_premium_assistance_target_contribution_percentage", period
        )
        income = max_(tax_unit("aca_magi", period), 0)
        amount = max_(0, benchmark * gross_up - target_percentage * income)
        plan_premium = add(tax_unit, period, ["nm_puente_health_plan_premium"])
        return min_(amount, plan_premium)
