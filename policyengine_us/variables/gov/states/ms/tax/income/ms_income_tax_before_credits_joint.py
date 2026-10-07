from policyengine_us.model_api import *


class ms_income_tax_before_credits_joint(Variable):
    value_type = float
    entity = Person
    label = "Mississippi income tax before credits when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        # Form 80-100 instructions, line 17: 2022 (page 7), 2023 (page 8), 2024 (page 7)
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=7",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100231.pdf#page=8",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100241.pdf#page=7",
    )

    def formula(person, period, parameters):
        income = person("ms_taxable_income_joint", period)
        rate = parameters(period).gov.states.ms.tax.income.rate
        # When one column is positive and the other negative, the two are
        # combined and the tax is computed on the net amount in Column A.
        is_head = person("is_tax_unit_head", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        tax_unit = person.tax_unit
        has_negative_column = tax_unit.any(head_or_spouse & (income < 0))
        combined_income = tax_unit.sum(head_or_spouse * income)
        combined_tax = is_head * rate.calc(max_(combined_income, 0))
        return where(has_negative_column, combined_tax, rate.calc(income))
