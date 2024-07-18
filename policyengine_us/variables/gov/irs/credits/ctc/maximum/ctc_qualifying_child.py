from policyengine_us.model_api import *


class ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "CTC-qualifying child"
    documentation = "Child qualifies for the Child Tax Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        age_limit = parameters(
            period
        ).gov.irs.credits.ctc.amount.base.thresholds[-1]
        age_eligible = age < age_limit
        return age_eligible & is_dependent
