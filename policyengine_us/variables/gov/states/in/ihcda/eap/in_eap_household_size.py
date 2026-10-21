from policyengine_us.model_api import *


class in_eap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Indiana EAP eligible household size"
    defined_for = StateCode.IN
    reference = (
        # Sections 3.2-3.3 (pages 23-25) and Sections 4.4-4.5 (pages 29-30).
        "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=23",
    )

    def formula(spm_unit, period, parameters):
        # SPM units approximate the residence-based unit. Section 3.2 counts roommates
        # and housemates as household members even when they are unrelated, and SPM
        # units place unrelated roommates in separate units. Current inputs cannot
        # identify all excluded foster children, exchange students, transient guests,
        # or changes in residence during the three-month budget period. Citizenship is
        # approximated by the existing qualified-status flag; SSN/document verification
        # is not modeled. Reported pregnancies count under Section 3.2.
        return add(
            spm_unit, period, ["is_citizen_or_legal_immigrant", "current_pregnancies"]
        )
