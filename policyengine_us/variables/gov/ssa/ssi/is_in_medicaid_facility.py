from policyengine_us.model_api import *


class is_in_medicaid_facility(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person resides in a Medicaid-funded nursing facility or ICF/IID"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382"
