from policyengine_us.model_api import *


class mt_social_security_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf"
    )
    defined_for = "mt_social_security_benefit_eligible"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mt.tax.income.subtractions

        exceeding_income = tax_unit(
            "mt_social_security_benefits_exceeding_income", period
        )  # line 11
        total_benefit_fraction1 = p.social_security.amount  # 0.5
        exceeding_income_cap = p.social_security.base_amount[
            filing_status
        ]  # line 12
        reduced_exceeding_income = max_(
            exceeding_income - exceeding_income_cap, 0
        )  # Line 13
        capped_exceeding_income = min_(
            exceeding_income, exceeding_income_cap
        )  # Line 14

        exceeding_income_fraction = (
            p.social_security.exceeding_income_fraction
        )  # 0.5

        net_benefits = tax_unit.spm_unit("spm_unit_benefits", period)
        halved_capped_income = (
            capped_exceeding_income * exceeding_income_fraction,
        )  # Line 15
        # Calculate the Montana Taxable Social Security Benefits
        capped_benefit_amount = min_(
            halved_capped_income,
            net_benefits * total_benefit_fraction1,
        )  # Line 16
        extra_income_fraction = p.social_security.extra_income_fraction  # 0.85
        reduced_exceeding_income_fraction = (
            reduced_exceeding_income * extra_income_fraction
        )  # Line 16
        total_income_and_benefit_amount = (
            reduced_exceeding_income_fraction + capped_benefit_amount
        )  # Line 18
        total_benefit_fraction2 = p.social_security.benefit  # 0.85
        net_benefit_fraction = (
            net_benefits * total_benefit_fraction2
        )  # Line 19
        return min_(total_income_and_benefit_amount, net_benefit_fraction)
