from policyengine_us.model_api import *


class wv_gross_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia gross household income"
    reference = (
        "https://code.wvlegislature.gov/11-21-23/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14"
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = (
        "gov.states.wv.tax.income.credits.heptc.gross_household_income.sources"
    )
