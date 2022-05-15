from openfisca_us.model_api import *


class is_medically_needy_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Is medically needy for Medicaid"
    documentation = "Whether this person qualifies for Medicaid under the 'medically needy' pathway. To qualify, a person must fit into another Medicaid category, and have income exceeding the limit, but income less medical expenses lower than a set of more restrictive limits."
    definition_period = YEAR

    def formula(person, period, parameters):
        pass
