from policyengine_us.model_api import *


class mt_medical_expense_deduction_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Montana medical expense deduction when married couples are filing separately"
    )
    reference = (
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=36",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)(g)(i)
    )
    unit = USD
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    documentation = (
        "Medical deduction after excluding the same person's self-employed "
        "health insurance premiums and applying the medical floor. Premium "
        "inputs use payer attribution: report all premiums paid by a person "
        "on that person, including family coverage regardless of the covered "
        "beneficiary."
    )

    def formula(person, period, parameters):
        premiums = person("medical_expense_health_insurance_premiums", period)
        se_health_insurance_ald = person(
            "self_employed_health_insurance_ald_person", period
        )
        # Separately computed medical expenses exclude the same person's
        # premiums already deducted from income.
        expense = max_(0, premiums - se_health_insurance_ald) + person(
            "other_medical_expenses", period
        )
        p = parameters(period).gov.irs.deductions.itemized.medical
        # Law does not define Montana AGI as the cap.
        # Tax form points to page 1, line 14, which is Montana AGI.
        medical_floor = p.floor * person("mt_agi_indiv", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return is_head_or_spouse * max_(0, expense - medical_floor)
