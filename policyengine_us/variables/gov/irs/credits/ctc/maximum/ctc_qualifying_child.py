from policyengine_us.model_api import *


class ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "CTC-qualifying child"
    documentation = "Child qualifies for the Child Tax Credit"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.irs.credits.ctc
        age_limit = p.amount.base.thresholds[-1]
        age_eligible = age < age_limit
        meets_identification_requirements = person(
            "meets_ctc_child_identification_requirements", period
        )
        return age_eligible & meets_identification_requirements
