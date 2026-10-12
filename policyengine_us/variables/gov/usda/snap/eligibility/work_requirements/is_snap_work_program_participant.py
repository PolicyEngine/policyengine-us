from policyengine_us.model_api import *


class is_snap_work_program_participant(Variable):
    value_type = bool
    entity = Person
    label = "SNAP work program participant"
    documentation = (
        "Whether this person participates in, or otherwise complies with, "
        "a SNAP employment and training program or workfare assignment. "
        "Under 7 CFR 273.7(a)(1), non-exempt work registrants must "
        "participate in an E&T program or workfare if assigned by the "
        "state agency. Willingness to participate alone does not satisfy "
        "this input when the person has an assignment requiring "
        "participation. This does not satisfy the ABAWD work requirement "
        "under 7 CFR 273.24, which requires actual hours of work or work "
        "program participation."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#a_1"
