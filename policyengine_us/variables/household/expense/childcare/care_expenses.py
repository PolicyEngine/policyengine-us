from policyengine_us.model_api import *


class care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Care expenses for a disabled adult dependent or spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#b_2"

    def formula(person, period, parameters):
        # No public subsidy applies to adult dependent care, so this passes
        # through the pre-subsidy amount (mirrors childcare_expenses).
        return person("pre_subsidy_care_expenses", period)
