from policyengine_us.model_api import *


class wv_social_security_benefits_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia social security benefits subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        # West Virginia Personal Income Tax Forms And Instructions 2020 LINE 33
        "https://tax.wv.gov/Documents/TaxForms/2020/it140.booklet.pdf#page=24",
        # West Virginia Personal Income Tax Forms And Instructions 2020 LINE 32
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24",
        # West Virginia Personal Income Tax Forms And Instructions 2022 LINE 32
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25",
        # Code of West Virginia §11-21-12 (c)(8)(A) - (c)(8)(C)
        "https://code.wvlegislature.gov/11-21-12/",
    )
    defined_for = "wv_social_security_benefits_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefits
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Federal adjusted gross income includes
        # social security benefits paid by the Social Security Administration as Old Age,
        # Survivors and Disability Insurance Benefits
        taxable_ss = person("taxable_social_security", period)
        total_eligible_ss = tax_unit.sum(taxable_ss * head_or_spouse)

        return total_eligible_ss * p.rate
