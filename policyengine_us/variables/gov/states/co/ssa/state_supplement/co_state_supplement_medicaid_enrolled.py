from policyengine_us.model_api import *


class co_state_supplement_medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid enrollment for the Colorado State Supplement deeming exemption"
    definition_period = YEAR
    # PDF page 95
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=95"
    documentation = (
        "Medicaid enrollment of an AND-CS client's spouse or parent, for the "
        "9 CCR 2503-5 3.549(F) deeming exemption. Under the Medicaid community "
        "engagement requirement, enrollment can turn on membership of a "
        "household receiving SNAP (42 CFR 435.554(c)(7)), and SNAP counts "
        "AND-CS as income. Enrollment is therefore computed in a private "
        "branch where this variable is false for everyone, so AND-CS deems "
        "every Medicaid spouse's or parent's income and is no higher than "
        "its final value, and SNAP is no lower."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        if not p.applies:
            return person("medicaid_enrolled", period)
        # The branch keeps the SNAP route to enrollment, and AND-CS inside it
        # reads this variable as an input, so nothing recurses. The parent
        # cannot hold this variable before computing it, so the branch
        # always shares the parent's cache, and the result does not depend
        # on whether SNAP, Medicaid or AND-CS is calculated first.
        simulation = person.simulation
        branch_name = f"{simulation.branch_name}_co_state_supplement_medicaid_{period}"
        try:
            branch = get_override_branch(
                simulation,
                branch_name,
                period,
                {
                    "co_state_supplement_medicaid_enrolled": np.zeros(
                        person.count, dtype=bool
                    )
                },
            )
            return branch.calculate("medicaid_enrolled", period)
        finally:
            # A branch clones cached arrays; retaining it would duplicate a
            # substantial part of a full-population simulation in memory.
            simulation.branches.pop(branch_name, None)
