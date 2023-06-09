from policyengine_us.model_api import *


class mi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MI standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction, consist of standard deduction for age 67-76, retirement and pension benefits for age 62-66 and above 77, and interest, dividends, and capital gains deduction for age above 77."
    reference = (
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.deductions.standard
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        age_older = max_(
            tax_unit("age_head", period), tax_unit("age_spouse", period)
        )
        # Michigan Standard Deduction
        age_min_threshold = p.min_age
        age_max_threshold = p.max_age
        aged_count = (
            age_older >= age_min_threshold and age_older <= age_max_threshold
        ).astype(int)
        amount_per_aged = p.amount[filing_status]
        standrad_deduction = aged_count * amount_per_aged

        # Retirement Benefits Deduction Tier 1
        tier1_age_threshold = p.retirement_benefits_deduction.tier_one.birth_year
        rb1_birth_year = -(age_older - period.start.year)
        rb1_age_eligibility = (rb1_birth_year < tier1_age_threshold).astype(int)
        rb1_amount_per_aged = p.retirement_benefits_deduction.tier_one.amount[
            filing_status
        ]
        rb1_deduction = rb1_age_eligibility * rb1_amount_per_aged

        # Retirement Benefits Deduction Tier 3
        tier3_age_min_threshold = p.retirement_benefits_deduction.tier_three.min_age
        tier3_age_max_threshold = p.retirement_benefits_deduction.tier_three.max_age
        rb3_age_eligibility = (
            age_older >= tier3_age_min_threshold
            and age_older <= tier3_age_max_threshold
        ).astype(int)
        rb3_amount_per_aged = p.retirement_benefits_deduction.tier_three.amount[
            filing_status
        ]
        rb3_deduction = (
            rb3_age_eligibility
            * rb3_amount_per_aged
            * tax_unit("mi_social_security_retirement", period)
        )

        # Interest, Dividends, and Capital Gains Deduction
        senior_age_threshold = (
            p.interest_dividends_capital_gains_deduction.senior_age
        )
        idcg_aged_count = (age_older >= senior_age_threshold).astype(int)
        idcg_amount_per_aged = (
            p.interest_dividends_capital_gains_deduction.senior_amount[
                filing_status
            ]
        )
        income = tax_unit("mi_interest_dividends_capital_gains_income", period)
        idcg_deduction = min_(idcg_aged_count * idcg_amount_per_aged, income)

        return (
            standrad_deduction + rb1_deduction + rb3_deduction + idcg_deduction
        )
