from policyengine_us.model_api import *


class pre_subsidy_care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Pre-subsidy care expenses for a disabled adult dependent or spouse"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/21#b_2"
