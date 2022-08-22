from openfisca_us.model_api import *

class mo_full_year_homestead(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO