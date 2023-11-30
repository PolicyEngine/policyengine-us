from policyengine_us.model_api import *


class mt_social_security_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2110/",
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=6",
    )
    defined_for = "mt_social_security_benefits_eligible"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.mt.tax.income.adjustments.social_security

        exceeding_income = tax_unit(
            "mt_social_security_benefits_exceeding_income", period
        )  # line 11
        exceeding_income_cap = p.cap[filing_status]  # line 12
        reduced_exceeding_income = max_(
            exceeding_income - exceeding_income_cap, 0
        )  # Line 13
        capped_exceeding_income = min_(
            exceeding_income, exceeding_income_cap
        )  # Line 14

        exceeding_income_fraction = (
            p.excess_income.exceeding_income_fraction
        ) 

        net_benefits = tax_unit.spm_unit("spm_unit_benefits", period)
        halved_capped_income = (
            capped_exceeding_income * exceeding_income_fraction,
        )  # Line 15
        total_benefit_fraction1 = p.fraction.income 
        capped_benefit_amount = min_(
            halved_capped_income,
            net_benefits * total_benefit_fraction1,
        )  # Line 16
        extra_income_fraction = p.fraction.total_income  
        reduced_exceeding_income_fraction = (
            reduced_exceeding_income * extra_income_fraction
        )  # Line 17
        total_income_and_benefit_amount = (
            reduced_exceeding_income_fraction + capped_benefit_amount
        )  # Line 18
        total_benefit_fraction2 = p.fraction.capped_income
        net_benefit_fraction = (
            net_benefits * total_benefit_fraction2
        )  # Line 19
        return min_(total_income_and_benefit_amount, net_benefit_fraction)
