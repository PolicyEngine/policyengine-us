from openfisca_us.model_api import *


class in_college_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN college credit for contributions to Indiana colleges and universities"
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-3-5" 
    
