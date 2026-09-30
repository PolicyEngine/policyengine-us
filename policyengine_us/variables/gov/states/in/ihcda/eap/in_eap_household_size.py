from policyengine_us.model_api import *


class in_eap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Indiana EAP eligible household size"
    defined_for = StateCode.IN
    reference = "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=23,24,25,29,30"

    def formula_2026(spm_unit, period, parameters):
        # SPM units approximate the residence-based unit. Current inputs cannot identify
        # all excluded foster children, exchange students, transient guests, or changes
        # in residence during the three-month budget period. Citizenship is approximated
        # by the existing qualified-status flag; SSN/document verification is not modeled.
        # Reported pregnancies count under Section 3.2.
        return add(
            spm_unit, period, ["is_citizen_or_legal_immigrant", "current_pregnancies"]
        )
