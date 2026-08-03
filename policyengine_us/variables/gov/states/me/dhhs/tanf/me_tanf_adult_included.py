from policyengine_us.model_api import *


class me_tanf_adult_included(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maine TANF assistance unit includes an adult"
    definition_period = YEAR
    documentation = (
        "Maine's chart applies the child-only schedule when no adult is in the "
        "assistance unit (an adult on SSI or non-parent caretaker is excluded "
        "from the unit); this proxies that with head/spouse presence net of SSI "
        "receipt, mirroring the Illinois TANF implementation."
    )
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/rule-2025-10/TANF%20125A%20Rule%20Pages%20%28Clean%29.pdf"
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        ssi = person("ssi", period)
        receives_ssi = (ssi > 0) | (add(person, period, ["receives_ssi"]) > 0)

        return spm_unit.any(is_head_or_spouse & ~receives_ssi)
