from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.aca_ptc_slcsp import (
    benchmark_premium,
)


class aca_ptc_coverage_family_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected Marketplace plan premium allocated to the coverage family"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-3#d_1"
    documentation = (
        "The enrollment premiums for the premium tax credit's lesser-of test "
        "(26 CFR 1.36B-3(d)(1)(i)). The model prices one policy per tax unit. "
        "When it also covers enrollees outside the tax family, 26 CFR "
        "1.36B-3(h)(1) allocates the premium 'in proportion to the premiums "
        "for each taxpayer's applicable benchmark plan': the coverage family's "
        "benchmark (aca_ptc_slcsp) over that plus the benchmark of the other "
        "enrollees, priced as one family of their own. The whole premium is "
        "the coverage family's when every enrollee is in it, and none is when "
        "no enrollee is. Each month's share is applied to that month's "
        "premium before summing, including for bronze plans. A supplied annual "
        "selected premium is distributed in proportion to the monthly "
        "selected-plan premium proxies, or evenly if those are unavailable."
    )

    def formula(tax_unit, period, parameters):
        premium = tax_unit("selected_marketplace_plan_premium_proxy", period)
        person = tax_unit.members
        enrolled = person("is_aca_marketplace_enrollee", period)
        member = person("is_aca_tax_family_member", period)
        any_enrollee_covered = tax_unit.any(enrolled & member)
        every_enrollee_covered = ~tax_unit.any(enrolled & ~member)
        months = period.get_subperiods(MONTH)
        monthly_premiums = [
            tax_unit("monthly_selected_marketplace_plan_premium_proxy", month)
            for month in months
        ]
        annual_proxy = sum(monthly_premiums)
        allocated_share = 0
        for month, monthly_premium in zip(months, monthly_premiums):
            # Preserve a supplied annual premium while retaining the monthly
            # price pattern. With derived inputs this is the month's actual
            # selected premium divided by the annual selected premium.
            month_weight = np.divide(
                monthly_premium,
                annual_proxy,
                out=np.full_like(annual_proxy, 1 / len(months)),
                where=annual_proxy > 0,
            )
            coverage_family_benchmark = tax_unit("aca_ptc_slcsp", month)
            other_benchmark = benchmark_premium(
                tax_unit, month, parameters, ~member, enrolled
            )
            total = coverage_family_benchmark + other_benchmark
            share = np.divide(
                coverage_family_benchmark,
                total,
                out=np.zeros_like(total),
                where=total > 0,
            )
            allocated_share += month_weight * share
        return where(
            any_enrollee_covered,
            premium * where(every_enrollee_covered, 1, allocated_share),
            0,
        )
