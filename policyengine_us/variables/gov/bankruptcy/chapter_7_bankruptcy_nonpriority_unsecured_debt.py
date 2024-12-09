from policyengine_us.model_api import *


class chapter_7_bankruptcy_nonpriority_unsecured_debt(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nonpriority unsecured debt"
    definition_period = YEAR
    reference = ("https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=9")
    documentation = "Line 41a in form 122A-2"
