from policyengine_us.model_api import *


class ne_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        fagi = tax_unit("adjusted_gross_income", period)
        taxable_oasdi = add(tax_unit, period, ["taxable_social_security"])
        p = parameters(period).gov.states.ne.tax.income.agi.subtractions
        return taxable_oasdi * p.oasdi_fraction(fagi)
