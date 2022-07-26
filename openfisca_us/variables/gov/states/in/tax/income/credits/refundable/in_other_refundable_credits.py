from openfisca_us.model_api import *


class in_other_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN other credits"
    definition_period = YEAR
    documentation = "Other refundable credits include the Lake County residential income tax credit, the economic development for a growing economy credit, the economic development for a growing economy retention credit, and the headquarters relocation credit refundable portion."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3.1" 
