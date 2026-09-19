from policyengine_us.model_api import *


class in_ssp_medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid enrollment for Indiana state supplement eligibility"
    definition_period = YEAR
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/ompp/files/Medicaid_PM_5000.pdf#page=2",
        "https://www.in.gov/fssa/ddars/bba/provider-resources/residential-care-assistance-program/",
        "https://www.ecfr.gov/current/title-42/section-435.554",
    )
    documentation = (
        "Medicaid enrollment condition for SAPN and RCAP candidates only. "
        "SSI recipients and aged, blind, or disabled RCAP candidates do not "
        "need the SNAP/TANF community-engagement exclusion. Other consumers "
        "must use medicaid_enrolled, which retains that exclusion."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        if not p.applies:
            return person("medicaid_enrolled", period)

        simulation = person.simulation
        enrolled = simulation.get_array("medicaid_enrolled", period)
        if enrolled is not None:
            return enrolled

        # SNAP counts Indiana SSP as income, so asking SNAP for its receipt
        # status here would recurse. SSP candidates qualify through SSI or
        # age/blindness/disability independently of SNAP/TANF. Keep all other
        # Medicaid conditions, take-up and supplied inputs in a private branch.
        branch_name = f"{simulation.branch_name}_in_ssp_medicaid_{period}"
        branch = simulation.get_branch(branch_name)
        try:
            branch.set_input(
                "medicaid_community_engagement_pass_through_eligible",
                period.first_month,
                np.zeros(person.count, dtype=bool),
            )
            return branch.calculate("medicaid_enrolled", period)
        finally:
            # A branch clones cached arrays; retaining it would duplicate a
            # substantial part of the full-population simulation in memory.
            simulation.branches.pop(branch_name, None)
