from openfisca_us.model_api import *


class mo_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-A_2021.pdf"

    def formula(tax_unit, period, parameters):
        
        #any itemizations 
        agi = tax_unit("adjusted_gross_income", period)
        additions = tax_unit("mo_additions", period)
        subtractions = tax_unit("mo_subtractions", period)

        return agi + additions - subtractions
