from policyengine_us.model_api import *


class va_tax_adjsutment_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Spouse Tax Adjustment"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        p1 = parameters(period).gov.states.va.tax.income

        person = tax_unit.members
        agi = person("va_agi", period)
        personal_va_agi = person(
            "va_prorate_fraction", period
        ) * person.tax_unit.sum(agi)
        personal_exemption_age_qualification = (
            person("age", period) >= p.age_threshold
        )
        personal_exemption_blind_qualification = person("is_blind", period)

        total_personal_exemptions = (
            personal_exemption_age_qualification
            + personal_exemption_blind_qualification
        ) * p.age_blind_multiplier + p.addition_amount

        eligibility_requirement = personal_va_agi - total_personal_exemptions

        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse

        min_eligibility_value = tax_unit.min_(
            head_or_spouse * eligibility_requirement
        )
        va_taxable_income = tax_unit("va_taxable_income", period)

        temp_value = max_(va_taxable_income - min_eligibility_value, 0)
        half_of_taxable_income = va_taxable_income / p.divider
        min_temp = p1.rates * min_(
            min_eligibility_value, half_of_taxable_income
        )
        max_temp = p1.rates * max_(temp_value, half_of_taxable_income)
        sum_amount = min_temp + max_temp

        tax_amount = tax_unit("va_income_tax", period)

        adjustent_limit_condition = (
            min_eligibility_value
            > p.threshold & tax_unit("va_taxable_income", period)
        )

        adjustment_amount = tax_amount - sum_amount
        tax_adjustment_amount = va_spouse_adjustment_qualification * min_(
            where(
                adjustment_limit_condition,
                p.adjustment_limit,
                adjustment_amount,
            ),
            p.adjustment_limit,
        )
        return tax_adjustment_amount
