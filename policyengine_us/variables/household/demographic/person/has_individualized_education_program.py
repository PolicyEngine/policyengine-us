from policyengine_us.model_api import *


class has_individualized_education_program(Variable):
    value_type = bool
    entity = Person
    label = "Has an Individualized Education Program (IEP)"
    definition_period = YEAR
    documentation = "Whether the child has an IEP under the Individuals with Disabilities Education Act (IDEA)"
