from policyengine_us.model_api import *


class aca_ptc_coverage_family_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected Marketplace plan premium allocated to the coverage family"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-3#d_1"
    documentation = (
        "The enrollment premiums for the premium tax credit's lesser-of test "
        "(26 CFR 1.36B-3(d)(1)(i)): the selected plan premium for the tax "
        "unit, of which the coverage family's share is its benchmark "
        "(aca_ptc_slcsp) over the whole enrollment's benchmark (slcsp). 26 "
        "CFR 1.36B-3(h)(1) allocates a policy covering more than one family "
        "'in proportion to the premiums for each taxpayer's applicable "
        "benchmark plan'; the whole-enrollment benchmark stands in for the "
        "sum of those benchmarks. The share is 1 whenever every enrollee is "
        "in the coverage family. It applies to bronze plans too."
    )

    def formula(tax_unit, period, parameters):
        premium = tax_unit("selected_marketplace_plan_premium_proxy", period)
        benchmark = add(tax_unit, period, ["slcsp"])
        coverage_family_benchmark = add(tax_unit, period, ["aca_ptc_slcsp"])
        share = np.divide(
            coverage_family_benchmark,
            benchmark,
            out=np.ones_like(benchmark),
            where=benchmark > 0,
        )
        return premium * share
