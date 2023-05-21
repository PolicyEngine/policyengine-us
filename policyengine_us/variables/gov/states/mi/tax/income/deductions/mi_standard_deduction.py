from policyengine_us.model_api import *


class mi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MI standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction, consist of standard deduction for age 67-76, retirement and pension benefits for age 61-66 and above 77, and interest, dividends, and capital gains deduction for age above 77."
    reference = (
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["mi"].tax.income.deductions.standard
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        # Michigan Standard Deduction
        age_min_threshold = p.min_age
        age_max_threshold = p.max_age
        age_older = max_(
            tax_unit("age_head", period), tax_unit("age_spouse", period)
        )
        # aged_head = (
        #     tax_unit("age_head", period) >= age_min_threshold
        #     and tax_unit("age_head", period) <= age_max_threshold
        # ).astype(int)
        # aged_spouse = (
        #     tax_unit("age_spouse", period) >= age_min_threshold
        #     and tax_unit("age_spouse", period) <= age_max_threshold
        # ).astype(int)
        aged_count = (
            age_older >= age_min_threshold and age_older <= age_max_threshold
        ).astype(int)
        amount_per_aged = p.amount[filing_status]
        standrad_deduction = aged_count * amount_per_aged

        # Retirement Benefits Deduction Tier 1
        tier1_age_threshold = p.retirement_benefits_deduction.tier1_age
        rb1_age_older = max_(
            tax_unit("age_head", period), tax_unit("age_spouse", period)
        )
        # rb1_aged_head = (
        #     tax_unit("age_head", period) >= tier1_age_threshold
        # ).astype(int)
        # rb1_aged_spouse = (
        #     tax_unit("age_spouse", period) >= tier1_age_threshold
        # ).astype(int)
        rb1_aged_count = (rb1_age_older >= tier1_age_threshold).astype(int)
        rb1_amount_per_aged = p.retirement_benefits_deduction.tier1_amount[
            filing_status
        ]
        rb1_deduction = rb1_aged_count * rb1_amount_per_aged

        # Retirement Benefits Deduction Tier 3
        tier3_age_min_threshold = p.retirement_benefits_deduction.tier3_min_age
        tier3_age_max_threshold = p.retirement_benefits_deduction.tier3_max_age
        rb3_age_older = max_(
            tax_unit("age_head", period), tax_unit("age_spouse", period)
        )
        # rb3_aged_head = (
        #     tax_unit("age_head", period) >= tier3_age_min_threshold
        #     and tax_unit("age_head", period) <= tier3_age_max_threshold
        # ).astype(int)
        # rb3_aged_spouse = (
        #     tax_unit("age_spouse", period) >= tier3_age_min_threshold
        #     and tax_unit("age_spouse", period) <= tier3_age_max_threshold
        # ).astype(int)
        rb3_aged_count = (
            rb3_age_older >= tier3_age_min_threshold
            and rb3_age_older <= tier3_age_max_threshold
        ).astype(int)
        rb3_amount_per_aged = p.retirement_benefits_deduction.tier3_amount[
            filing_status
        ]
        rb3_deduction = rb3_aged_count * rb3_amount_per_aged

        # Interest, Dividends, and Capital Gains Deduction
        senior_age_threshold = (
            p.interest_dividends_capital_gains_deduction.senior_age
        )
        idcg_age_older = max_(
            tax_unit("age_head", period), tax_unit("age_spouse", period)
        )
        # idcg_aged_head = (
        #     tax_unit("age_head", period) >= senior_age_threshold
        # ).astype(int)
        # idcg_aged_spouse = (
        #     tax_unit("age_spouse", period) >= senior_age_threshold
        # ).astype(int)
        idcg_aged_count = (idcg_age_older >= senior_age_threshold).astype(int)
        idcg_amount_per_aged = (
            p.interest_dividends_capital_gains_deduction.senior_amount[
                filing_status
            ]
        )
        idcg_deduction = idcg_aged_count * idcg_amount_per_aged

        return (
            standrad_deduction + rb1_deduction + rb3_deduction + idcg_deduction
        )
