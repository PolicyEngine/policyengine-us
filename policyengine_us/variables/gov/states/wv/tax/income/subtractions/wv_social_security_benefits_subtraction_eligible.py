from policyengine_us.model_api import *


class wv_social_security_benefits_subtraction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for the West Virginia social security benefits subtraction"
    )
    definition_period = YEAR
    reference = (
        # West Virginia Personal Income Tax Forms And Instructions 2020 LINE 33
        "https://tax.wv.gov/Documents/TaxForms/2020/it140.booklet.pdf#page=24",
        # West Virginia Personal Income Tax Forms And Instructions 2020 LINE 32
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24",
        # West Virginia Personal Income Tax Forms And Instructions 2022 LINE 32
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25",
        # Code of West Virginia §11-21-12 (c)(8)(D)
        "https://code.wvlegislature.gov/11-21-12/",
    )
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefits
        return agi <= p.income_limit[filing_status]
