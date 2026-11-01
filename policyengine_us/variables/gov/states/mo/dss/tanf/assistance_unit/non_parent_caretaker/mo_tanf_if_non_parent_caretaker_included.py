from policyengine_us.model_api import *


class mo_tanf_if_non_parent_caretaker_included(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF grant if a needy non-parent caretaker is included"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-15/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Budget the whole program with the caretaker in the group when
        # they are needy, in a private branch so every test and deduction
        # follows the same code path as mo_tanf itself.
        needy = spm_unit("mo_tanf_non_parent_caretaker_needy", period)
        simulation = spm_unit.simulation
        branch_name = f"{simulation.branch_name}_mo_tanf_npcr_included_{period}"
        try:
            branch = get_override_branch(
                simulation,
                branch_name,
                period,
                {"mo_tanf_non_parent_caretaker_included": needy},
            )
            return branch.calculate("mo_tanf", period)
        finally:
            # A branch clones cached arrays; drop it once the grant is read.
            simulation.branches.pop(branch_name, None)
