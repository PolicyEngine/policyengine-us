from policyengine_us.model_api import *


class wv_low_income_earned_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia low-income earned income exclusion"
    defined_for = "wv_low_income_earned_income_exclusion_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-10/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=20"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=27"
    )

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        earned_income = tax_unit("tax_unit_earned_income", period)
        filing_status = tax_unit("filing_status", period)

        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.low_income_earned_income
        # Lesser of federal AGI, earned income, and exclusion cap.
        income_min = min_(federal_agi, earned_income)
        return min_(income_min, p.amount[filing_status])
