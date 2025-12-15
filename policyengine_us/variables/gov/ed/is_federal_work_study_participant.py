from policyengine_us.model_api import *


class is_federal_work_study_participant(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Participating in Federal Work Study"
    reference = "https://www.law.cornell.edu/cfr/text/34/part-675"
