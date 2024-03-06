from policyengine_us.model_api import *


class vt_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf (Line 3)"

    adds = ["adjusted_gross_income", "vt_agi_additions"]
    subtracts = ["vt_subtractions"]
