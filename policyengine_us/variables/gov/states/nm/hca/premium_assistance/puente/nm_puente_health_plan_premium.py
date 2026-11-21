from policyengine_us.model_api import *


class nm_puente_health_plan_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Puente Health selected plan premium"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = (
        # Addendum 2: "A consumer's net premium cannot be lower than $0" when
        # the assistance exceeds "the gross premium of the plan selected by the
        # consumer" (PY2026).
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/3527710a-f9f6-4e8f-9cd7-d9ea1010b653/Addendum%202_%20MAP%20P%26P%20Puente%20Health.pdf#page=3",
        # FINAL PY2027 MAP manual: the same $0 floor (p.5), applied to Puente
        # Health by the manual's Calculating Monthly Puente Health Premium
        # Assistance Payments section (p.8).
        # PDF pages 5, 8
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/b61d3073-c0e6-4426-bb40-4cfef26fdca4/FINAL%202027%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=5",
    )
    documentation = (
        "The monthly gross premium of the plan the tax unit's Puente Health "
        "members select, which caps Puente Health premium assistance at a $0 "
        "net premium. It follows the plan selection inputs of "
        "monthly_selected_marketplace_plan_premium_proxy, priced for the "
        "Puente Health members, whom that variable leaves out: a silver plan "
        "is the members' benchmark times "
        "selected_marketplace_plan_benchmark_ratio, and a bronze plan is the "
        "members' lowest-cost bronze premium. New Mexico rates both metal "
        "levels on the same default age curve, so that bronze premium is the "
        "members' benchmark times the rating area's bronze-to-silver premium "
        "at age 0. Take-up "
        "is not applied here; assigned_nm_puente_health_premium_assistance "
        "applies it."
    )

    def formula(tax_unit, period, parameters):
        year = period.this_year
        benchmark = tax_unit("nm_puente_health_benchmark_premium", period)
        silver = benchmark * tax_unit("selected_marketplace_plan_benchmark_ratio", year)
        silver_age_0 = tax_unit.household("slcsp_age_0", period)
        bronze_age_0 = tax_unit.household("lcbp_age_0", period)
        bronze_share = np.divide(
            bronze_age_0,
            silver_age_0,
            out=np.zeros_like(silver_age_0),
            where=silver_age_0 > 0,
        )
        category = tax_unit("selected_marketplace_plan_category", year)
        return where(
            category == category.possible_values.BRONZE,
            benchmark * bronze_share,
            silver,
        )
