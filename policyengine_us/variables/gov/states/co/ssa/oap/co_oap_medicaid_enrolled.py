from policyengine_us.model_api import *


class co_oap_medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid enrollment for the Colorado Old Age Pension deeming exemption"
    definition_period = YEAR
    reference = (
        # 9 CCR 2503-5 3.534(C)
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=78",
        "https://www.ecfr.gov/current/title-42/section-435.554#p-435.554(c)(7)",
    )

    def formula(person, period, parameters):
        # Reported current coverage counts as receiving Medicaid assistance
        # (3.534(C)) whatever projected eligibility and take-up say.
        reported = person("receives_medicaid", period)
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        if not p.applies:
            return person("medicaid_enrolled", period) | reported

        # SNAP counts OAP as income, and Medicaid's SNAP pass-through from the
        # community engagement requirement (42 CFR 435.554(c)(7)) reads SNAP
        # receipt, so OAP, a spouse's Medicaid enrollment and SNAP depend on
        # each other. Medicaid is computed in a private branch where only
        # reported coverage exempts a spouse's income from OAP deeming:
        # enrollment is decided on the SNAP the household receives while the
        # other spouses' income is still deemed, before an exemption raises
        # OAP. The spouse keeps every Medicaid route, supplied inputs
        # included, and the result does not depend on calculation order.
        # In a SNAP unit with one spouse whose exemption turns on this, higher
        # OAP can only lower SNAP, so at most one outcome is self-consistent,
        # and this finds it when it exists; when none exists (the exemption's
        # higher OAP would end the SNAP receipt that gave the spouse Medicaid),
        # it treats the spouse as enrolled. With several such spouses in one
        # SNAP unit, enrollment is decided with all of their income deemed,
        # which need not be self-consistent.
        simulation = person.simulation
        branch_name = f"{simulation.branch_name}_co_oap_medicaid_{period}"
        try:
            branch = get_override_branch(
                simulation,
                branch_name,
                period,
                {"co_oap_medicaid_enrolled": np.asarray(reported, dtype=bool)},
            )
            return branch.calculate("medicaid_enrolled", period) | reported
        finally:
            # A branch clones cached arrays; retaining it would duplicate a
            # substantial part of the full-population simulation in memory.
            simulation.branches.pop(branch_name, None)
