from policyengine_us.model_api import *


class nm_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico standard deduction"
    unit = USD
    documentation = 'https://www.irs.gov/instructions/i1040gi#en_US_2022_publink24811vd0e10057'
    definition_period = YEAR
    defined_for = StateCode.NM
    adds = ["standard_deduction"]
