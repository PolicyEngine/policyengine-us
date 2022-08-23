from openfisca_us.model_api import *

class mo_resident_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO resident tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-CR_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        mo_agi = tax_unit("adjusted_gross_income",period)
