from policyengine_us.model_api import *


class ca_la_infant_supplement_eligible_infant(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible Infant for the Los Angeles County infant supplement"
    defined_for = "in_la"
    reference = "https://cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2021/21-123.pdf?ver=2021-10-08-140950-570"

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        dependent = person("is_tax_unit_dependent", period)
        return ~head_or_spouse & ~dependent
