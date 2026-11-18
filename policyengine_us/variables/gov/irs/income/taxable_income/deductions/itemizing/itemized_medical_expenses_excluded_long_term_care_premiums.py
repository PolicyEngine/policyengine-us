from policyengine_us.model_api import *


class itemized_medical_expenses_excluded_long_term_care_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employed long-term care premiums excluded from Schedule A"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_C",
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=2",
    ]
    documentation = (
        "The part of the federal self-employed health insurance deduction "
        "left after the head's and spouse's medical insurance premiums "
        "(itemized_medical_expenses_excluded_premiums), limited to their "
        "eligible long-term care premiums. 26 U.S.C. 162(l)(3) keeps premiums "
        "taken as that deduction off Schedule A. The split is for the return "
        "as a whole: it takes the deduction from the head's and spouse's "
        "pooled medical insurance premiums first, so it can book one filer's "
        "long-term care deduction against the other filer's medical premiums. "
        "Any split leaves the Schedule A subtotal unchanged. A supplied "
        "subtotal carries only the total exclusion, and Montana's 2021-2023 "
        "schedule recovers its medical part by this same pooled rule, so the "
        "computed and supplied paths agree. Each person's own long-term care "
        "part is self_employed_health_insurance_ald_long_term_care_part."
    )

    def formula(tax_unit, period, parameters):
        filer_premiums = tax_unit_non_dep_sum(
            "eligible_long_term_care_premiums", tax_unit, period
        )
        deduction = max_(0, tax_unit("self_employed_health_insurance_ald", period))
        medical_premiums = tax_unit(
            "itemized_medical_expenses_excluded_premiums", period
        )
        return min_(filer_premiums, deduction - medical_premiums)
