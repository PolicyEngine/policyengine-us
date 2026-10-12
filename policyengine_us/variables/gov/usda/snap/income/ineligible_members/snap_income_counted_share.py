from policyengine_us.model_api import *


class snap_income_counted_share(Variable):
    value_type = float
    entity = Person
    label = "SNAP share of income counted toward the household"
    definition_period = MONTH
    unit = "/1"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.11#d",
    )

    def formula(person, period, parameters):
        student = person("is_snap_ineligible_student", period.this_year)
        prorated = person("is_snap_prorated_income_member", period)
        fraction = person.spm_unit("snap_prorated_income_fraction", period)
        return select([student, prorated], [0, fraction], default=1)
