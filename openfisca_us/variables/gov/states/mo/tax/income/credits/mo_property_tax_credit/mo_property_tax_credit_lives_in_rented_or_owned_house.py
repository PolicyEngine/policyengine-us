from openfisca_us.model_api import *


class mo_property_tax_credit_lives_in_rented_or_owned_house(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit rent or own status"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435",
    )
    defined_for = StateCode.MO
