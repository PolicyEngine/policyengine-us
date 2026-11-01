from policyengine_us.model_api import *


class mo_tanf_non_parent_caretaker_opts_out(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF non-parent caretaker opts out of the assistance group"
    documentation = (
        "Whether a needy non-parent caretaker relative or legal guardian "
        "chooses to be excluded from the Temporary Assistance group, for "
        "example to avoid using their own time-limited months. When false, "
        "the caretaker is included whenever inclusion neither makes the unit "
        "ineligible nor reduces the grant."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-300",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-15/",
    )
    defined_for = StateCode.MO
