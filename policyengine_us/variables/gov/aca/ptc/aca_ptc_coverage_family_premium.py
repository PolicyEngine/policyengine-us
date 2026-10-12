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
        "no enrollee is. It applies to bronze plans too."
    )

    def formula(tax_unit, period, parameters):
        premium = tax_unit("selected_marketplace_plan_premium_proxy", period)
        person = tax_unit.members
        enrolled = person("is_aca_marketplace_enrollee", period)
        member = person("is_aca_tax_family_member", period)
        every_enrollee_covered = ~tax_unit.any(enrolled & ~member)
        coverage_family_benchmark = add(tax_unit, period, ["aca_ptc_slcsp"])
        other_benchmark = sum(
            benchmark_premium(tax_unit, month, parameters, ~member, enrolled)
            for month in period.get_subperiods(MONTH)
        )
        total = coverage_family_benchmark + other_benchmark
        share = np.divide(
            coverage_family_benchmark,
            total,
            out=np.zeros_like(total),
            where=total > 0,
        )
        return premium * where(every_enrollee_covered, 1, share)
