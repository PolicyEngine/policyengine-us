from policyengine_us.model_api import *


class aca_ptc_slcsp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Benchmark silver-plan premium for the premium tax credit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#b_3_B",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-3#f",
    )
    documentation = (
        "The second-lowest-cost silver plan premium offered to the coverage "
        "family (26 CFR 1.36B-3(f)): the enrollees who are in the premium tax "
        "credit tax family. When every enrollee on the return is in it, this "
        "is slcsp itself, read directly so a supplied slcsp carries through. "
        "When an enrollee is not (one who can be claimed on another return, "
        "or a dependent of a return with such a filer), it is the age-curve "
        "premiums of the coverage family members or, where family tiers "
        "apply, the tier premium for them. slcsp keeps every enrollee, since "
        "everyone still buys a plan."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        enrolled = person("pays_aca_premium", period.this_year)
        covered = person("is_aca_coverage_family_member", period.this_year)
        every_enrollee_covered = ~tax_unit.any(enrolled & ~covered)
        age_curve = tax_unit.sum(
            covered * person("slcsp_age_curve_amount_person", period)
        )
        family_tier = tax_unit.household("slcsp_age_0", period) * tax_unit(
            "aca_ptc_slcsp_family_tier_multiplier", period
        )
        coverage_family_benchmark = age_curve + family_tier
        return where(
            every_enrollee_covered,
            tax_unit("slcsp", period),
            coverage_family_benchmark,
        )
