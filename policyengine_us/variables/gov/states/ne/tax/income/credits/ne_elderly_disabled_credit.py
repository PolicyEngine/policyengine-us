from policyengine_us.model_api import *


class ne_elderly_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE elderly/disabled tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        credit = tax_unit("elderly_disabled_credit", period)
        us_itax_before_credits = tax_unit("income_tax_before_credits", period)
        return min_(credit, us_itax_before_credits)
