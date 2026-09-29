from policyengine_us.model_api import *


class mo_tanf_if_non_parent_caretaker_excluded(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF grant if the non-parent caretaker is excluded"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-15/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Budget the whole program without the caretaker (needs, income and
        # resources), in a private branch; see
        # mo_tanf_if_non_parent_caretaker_included.
        simulation = spm_unit.simulation
        branch_name = f"{simulation.branch_name}_mo_tanf_npcr_excluded_{period}"
        branch = simulation.get_branch(branch_name)
        try:
            branch.set_input(
                "mo_tanf_non_parent_caretaker_included",
                period,
                np.zeros(spm_unit.count, dtype=bool),
            )
            return branch.calculate("mo_tanf", period)
        finally:
            simulation.branches.pop(branch_name, None)
