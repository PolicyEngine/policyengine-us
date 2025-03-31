from policyengine_us.model_api import *


class in_healthcare_sharing_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana healthcare sharing ministry deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Healthcare sharing expenses paid by a qualified individual for membership in a health care sharing ministry allowable for deduction in Indiana."
    reference = "https://iga.in.gov/laws/2024/ic/titles/6#6-3-2-28"
    defined_for = StateCode.IN
