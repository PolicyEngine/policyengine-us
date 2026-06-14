from policyengine_us.model_api import *


class ca_oc_general_relief_eligible_person_count(Variable):
    value_type = int
    entity = SPMUnit
    label = "Orange County General Relief eligible person count"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = (
        "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=4"
    )
    # The MAP is based on the number of eligible persons in the GR Economic
    # Unit: children and members excluded for SSI/SSP, noncitizen status, or
    # another Sec 20.4 reason such as CAPI are not counted (Sec 80.2.d,
    # Sec 80.3.a(2)). For members on CalWORKs/RCA, Sec 80.3.a(1) instead
    # prescribes MAP differencing -- MAP(all members) less MAP(CalWORKs/RCA
    # members) -- but that mixed case cannot arise here: CalWORKs/CAPI receipt
    # is tracked at the SPM-unit level, so a unit receiving it has no eligible
    # person and is categorically ineligible.
    adds = ["ca_oc_general_relief_eligible_person"]
