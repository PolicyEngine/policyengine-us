from policyengine_us.model_api import *


class is_snap_work_requirements_disqualified(Variable):
    value_type = bool
    entity = Person
    label = "SNAP work requirements disqualified"
    documentation = (
        "Whether this person is individually disqualified from the SNAP "
        "unit for failing the general work requirements. Per 7 CFR "
        "273.7(f)(1), the disqualified member is excluded from the SNAP "
        "unit; remaining members continue to receive SNAP."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#f_1"

    def formula(person, period, parameters):
        return ~person("meets_snap_general_work_requirements", period)
