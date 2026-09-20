from policyengine_us.model_api import *


class ca_calworks_child_care_has_qualifying_court_supervision(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    defined_for = StateCode.CA
    label = "California CalWORKs child-care qualifying juvenile court supervision"
    documentation = "Whether the reported court supervision is under Welfare and Institutions Code section 300, 301, 601, or 602, as required by MPP 47-201.23 for Stage One child care."
    reference = "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/14EAS.pdf#page=34"
