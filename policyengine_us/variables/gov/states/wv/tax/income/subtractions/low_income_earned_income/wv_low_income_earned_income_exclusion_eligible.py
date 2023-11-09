from policyengine_us.model_api import *


class wv_low_income_earned_income_exclusion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia low-income earned income exclusion"
    defined_for = StateCode.WV
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-10/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=20"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=27"
    )

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.low_income_earned_income

        return federal_agi <= p.income_limit[filing_status]
