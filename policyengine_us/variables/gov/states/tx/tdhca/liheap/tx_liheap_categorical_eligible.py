from policyengine_us.model_api import *


class tx_liheap_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Texas LIHEAP categorically eligible"
    documentation = (
        "Determines categorical eligibility for Texas LIHEAP through "
        "receipt of SNAP, TANF, or SSI benefits"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Check SNAP receipt
        snap = spm_unit("snap", period)
        receives_snap = snap > 0

        # Check TANF receipt
        tanf = spm_unit("tanf", period)
        receives_tanf = tanf > 0

        # Check SSI receipt for any member
        person = spm_unit.members
        ssi = person("ssi", period.this_year)
        receives_ssi = spm_unit.any(ssi > 0)

        # Categorically eligible if receiving any of these programs
        return receives_snap | receives_tanf | receives_ssi