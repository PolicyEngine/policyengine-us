from policyengine_us.model_api import *


class mo_tanf_non_parent_caretaker_included(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF non-parent caretaker included in the assistance group"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-300",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-15/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # A non-needy NPCR is excluded outright: "When the NPCR is
        # determined to be not needy, exclude the NPCR from the Temporary
        # Assistance assistance group (both needs and income)" (DSS Manual
        # 0210.005.35).
        needy = spm_unit("mo_tanf_non_parent_caretaker_needy", period)
        # A needy NPCR "has the option of being included or excluded"
        # (0210.005.35; 13 CSR 40-2.300(5)(D)).
        person = spm_unit.members
        npcr = person("mo_tanf_non_parent_caretaker", period)
        opts_out = person("mo_tanf_non_parent_caretaker_opts_out", period.this_year)
        may_be_included = needy & ~spm_unit.any(npcr & opts_out)
        if not may_be_included.any():
            return may_be_included
        # Optional members are limited by DSS Manual 0210.005.15: "Do not
        # include an optional person if their inclusion causes
        # ineligibility or a reduction in the grant." Both groups are
        # budgeted in full, and the caretaker is included only when that
        # yields a payable grant at least as large as the children's grant
        # alone. When both are zero the caretaker is left out. The choice
        # is one per SPM unit, so two caretakers in one SPM unit are
        # included or excluded together.
        grant_if_included = spm_unit("mo_tanf_if_non_parent_caretaker_included", period)
        grant_if_excluded = spm_unit("mo_tanf_if_non_parent_caretaker_excluded", period)
        return (
            may_be_included
            & (grant_if_included > 0)
            & (grant_if_included >= grant_if_excluded)
        )
