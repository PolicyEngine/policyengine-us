from policyengine_us.model_api import *


class fl_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Florida LIHEAP household size"
    defined_for = StateCode.FL
    reference = "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=42"

    # Manual 900.04A (page 41) makes a household eligible when "at least one
    # member, preferably an adult," qualifies, but 900.04D.1 denies the
    # application when "The applicant is an illegal alien". No input names
    # the applicant, so a qualified member is assumed to apply.
    # Ineligible members are excluded from size, but their otherwise countable
    # income remains included in full. SPM membership approximates the energy
    # economic unit; roomers, separate energy units, special status documents,
    # and tribal-provider assignments are not completely identified by inputs.
    adds = ["is_citizen_or_legal_immigrant"]
