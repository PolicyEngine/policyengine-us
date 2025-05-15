from policyengine_us.model_api import *


class wv_social_security_benefits_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = (
        "West Virginia social security benefits subtraction for each person"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # West Virginia Personal Income Tax Forms And Instructions 2020 LINE 33
        "https://tax.wv.gov/Documents/TaxForms/2020/it140.booklet.pdf#page=24",
        # West Virginia Personal Income Tax Forms And Instructions 2020 LINE 32
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24",
        # West Virginia Personal Income Tax Forms And Instructions 2022 LINE 32
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25",
        # Code of West Virginia §11-21-12 (c)(8)(A) - (c)(8)(F)
        "https://code.wvlegislature.gov/11-21-12/",
    )
    defined_for = StateCode.WV

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefits
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Federal adjusted gross income includes
        # social security benefits paid by the Social Security Administration as Old Age,
        # Survivors and Disability Insurance Benefits
        taxable_ss = person("taxable_social_security", period)
        amount_if_eligible = taxable_ss * p.rate
        base_amount = amount_if_eligible * head_or_spouse
        eligible = person.tax_unit(
            "wv_social_security_benefits_subtraction_eligible", period
        )
        if p.social_security_benefits_above_income_limit.applies:
            multiplier = where(
                eligible, 1, p.social_security_benefits_above_income_limit.rate
            )
            return base_amount * multiplier
        return base_amount * eligible
