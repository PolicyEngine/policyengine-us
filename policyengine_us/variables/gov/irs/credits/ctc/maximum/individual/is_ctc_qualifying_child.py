from policyengine_us.model_api import *


class is_ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Is a CTC-qualifying child"
    documentation = "Is a child qualifying for the Child Tax Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        p = parameters(period).policyengine_us.gov.irs.credits.ctc
        qualifies_age = age <= p.child.ineligible_age
        return dependent & qualifies_age
