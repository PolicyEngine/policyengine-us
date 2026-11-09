from policyengine_us.model_api import *


class co_adult_financial_medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid enrollment for the Colorado Adult Financial deeming exemptions"
    documentation = (
        "Medicaid enrollment of the spouse or parent of a Colorado Old Age "
        "Pension or AND-CS client, for the 9 CCR 2503-5 3.534(C) and 3.549(F) "
        "deeming exemptions. Under the Medicaid community engagement "
        "requirement, enrollment can turn on membership of a household "
        "receiving SNAP (42 CFR 435.554(c)(7)), and SNAP counts both grants "
        "as income, so enrollment is computed in one private branch shared "
        "by both programs."
    )
    definition_period = YEAR
    reference = (
        # 9 CCR 2503-5 3.534(C), PDF page 78
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=78",
        # 9 CCR 2503-5 3.549(F), PDF page 95
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=95",
        "https://www.ecfr.gov/current/title-42/section-435.554#p-435.554(c)(7)",
    )

    def formula(person, period, parameters):
        # Reported current coverage counts as "receiving ... Medicaid"
        # (3.534(C), 3.549(F)) whatever projected eligibility and take-up say.
        reported = person("receives_medicaid", period)
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        if not p.applies:
            return person("medicaid_enrolled", period) | reported

        # SNAP counts OAP and AND-CS as income, and Medicaid's SNAP
        # pass-through from the community engagement requirement
        # (42 CFR 435.554(c)(7)) reads SNAP receipt, so both grants, a
        # spouse's or parent's Medicaid enrollment and SNAP depend on each
        # other. Medicaid is computed in a private branch where only reported
        # coverage exempts income from OAP or AND-CS deeming: enrollment is
        # decided on the SNAP the household receives while the other spouses'
        # and parents' income is still deemed, before an exemption raises
        # either grant. One variable serves both programs, so neither opens a
        # branch inside the other's. The spouse keeps every Medicaid route,
        # supplied inputs included, and the result does not depend on
        # calculation order. Where a single unresolved exemption is all that
        # links a group of households through SNAP units and marriages, a
        # higher grant can only lower SNAP, so at most one outcome is
        # self-consistent, and this finds it when it exists; when none exists
        # (the exemption's higher grant would end the SNAP receipt that gave
        # the spouse Medicaid), it treats the spouse as enrolled. With several
        # unresolved exemptions linked that way, enrollment is decided with
        # all of their income deemed, which need not be self-consistent.
        simulation = person.simulation
        branch_name = f"{simulation.branch_name}_co_adult_financial_medicaid_{period}"
        try:
            branch = get_override_branch(
                simulation,
                branch_name,
                period,
                {
                    "co_adult_financial_medicaid_enrolled": np.asarray(
                        reported, dtype=bool
                    )
                },
            )
            return branch.calculate("medicaid_enrolled", period) | reported
        finally:
            # A branch clones cached arrays; retaining it would duplicate a
            # substantial part of the full-population simulation in memory.
            simulation.branches.pop(branch_name, None)
