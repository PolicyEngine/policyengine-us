from policyengine_us.model_api import *


class is_snap_work_program_participant(Variable):
    value_type = bool
    entity = Person
    label = "SNAP work program participant"
    documentation = (
        "Whether this person participates in, or is willing to participate "
        "in, a SNAP employment and training program or workfare. Actual "
        "participation is not required: under 7 CFR 273.7(a)(1), a work "
        "registrant only has to participate if the state assigns them, and "
        "disqualification under 7 CFR 273.7(f) applies only to those who "
        "refuse to comply without good cause. Willingness to comply "
        "therefore satisfies the general work requirements. This does not "
        "satisfy the ABAWD work requirement under 7 CFR 273.24, which "
        "requires actual hours of work or work program participation."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#a_1"
