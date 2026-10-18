from policyengine_us.model_api import *


class mt_premium_deduction_joint(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Montana insurance premiums deducted in full on a joint return"
    documentation = (
        "Itemized Deductions Schedule lines 2 and 3 for a single-column "
        "return (2021-2023): medical and long-term care insurance premiums "
        "deducted in full, except premiums already deducted. The "
        "self-employed health insurance deduction reported for the return "
        "(Schedule 1, line 17, for premiums the head and spouse paid) is "
        "netted from their premiums once: first from medical insurance "
        "premiums, by the same bounded exclusion the computed federal "
        "Schedule A subtotal uses, then from long-term care premiums. A "
        "deduction supplied for the return is honored. A dependent's "
        "deduction belongs on the dependent's own return and is netted from "
        "that dependent's premiums. Premium inputs use payer attribution."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33",
        # MCA 2021 § 15-30-2131(1)(a)(iii)-(iv) and (1)(g)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        # 26 U.S.C. 162(l)(2)(C) and (l)(3)
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_C",
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        premiums = tax_unit_non_dep_sum(
            "medical_expense_health_insurance_premiums", tax_unit, period
        )
        long_term_care_premiums = tax_unit_non_dep_sum(
            "long_term_health_insurance_premiums", tax_unit, period
        )
        deduction = max_(0, tax_unit("self_employed_health_insurance_ald", period))
        # The bounded exclusion the computed federal subtotal applies to these
        # premiums: min(premiums, deduction).
        used_on_line_2 = tax_unit("itemized_medical_expenses_excluded_premiums", period)
        filer_amount = (
            premiums
            - used_on_line_2
            + max_(0, long_term_care_premiums - (deduction - used_on_line_2))
        )
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        dependent_amount = tax_unit.sum(
            is_dependent
            * (
                person("mt_eligible_medical_insurance_premiums", period)
                + person("mt_eligible_long_term_care_insurance_premiums", period)
            )
        )
        return filer_amount + dependent_amount
