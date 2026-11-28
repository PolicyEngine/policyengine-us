from policyengine_us.model_api import *


class meets_medicaid_adult_group_child_coverage_requirement(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Medicaid adult group child coverage requirement"
    documentation = (
        "42 CFR 435.119(c): a parent or other caretaker relative living with "
        "a child under the state's age limit qualifies for the adult group "
        "only if each such child has Medicaid, Children's Health Insurance "
        "Program, Marketplace or other minimum essential coverage. People "
        "who are not a parent or caretaker of such a child meet the "
        "requirement."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.119#c",
        "https://www.law.cornell.edu/uscode/text/42/1396a#k_3",
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/NJ/NJ-13-0011-MM1.pdf#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.adult.child_coverage
        state = person.household("state_code_str", period)
        # 42 CFR 435.119(c)(1) reaches a parent or caretaker relative "living
        # with a dependent child if the child is under the age specified in
        # paragraph (c)(2)". The (c)(2) age (19, or the state's 20 or 21)
        # applies, not the 42 CFR 435.4 dependent-child age of under 18,
        # which would leave (c)(2) without effect; New Jersey's S32 page
        # reads "a child under the age specified" and 42 U.S.C. 1396a(k)(3)
        # "a child who is under 19 years of age (or such higher age as the
        # State may have elected)". The 435.4 deprivation test does not
        # apply either. The caretaker relationship is the parent group's
        # tax-unit proxy, so a child who files their own return, such as a
        # 19- or 20-year-old living at home, is not counted.
        age = person("age", period)
        in_care = person("is_child_of_medicaid_caretaker", period)
        child_under_age = in_care & (age < p.age_limit[state])
        is_dependent = person("is_tax_unit_dependent", period)
        is_caretaker = person("is_tax_unit_head_or_spouse", period) & ~is_dependent
        lives_with_child_under_age = is_caretaker & person.tax_unit.any(child_under_age)
        if not lives_with_child_under_age.any():
            return np.ones(person.count, dtype=bool)

        # A child's Medicaid, CHIP and Marketplace status each depend on
        # medicaid_category, which evaluates the adult group, and so this
        # requirement, for everyone. They are computed in a private branch
        # where the requirement is met. That changes nothing for the children:
        # only a non-dependent head or spouse is a caretaker, so a tax-unit
        # dependent always meets the requirement.
        simulation = person.simulation
        branch_name = (
            f"{simulation.branch_name}_medicaid_adult_group_child_coverage_{period}"
        )
        try:
            branch = get_override_branch(
                simulation,
                branch_name,
                period,
                {
                    "meets_medicaid_adult_group_child_coverage_requirement": np.ones(
                        person.count, dtype=bool
                    )
                },
            )
            covered = branch.calculate(
                "has_child_coverage_for_medicaid_adult_group", period
            )
        finally:
            # A branch clones cached arrays; retaining it would duplicate a
            # substantial part of the full-population simulation in memory.
            simulation.branches.pop(branch_name, None)

        # Every child under the age counts, including one eligible for none
        # of Medicaid, CHIP or the Marketplace, as 42 CFR 435.119(c)(1), the
        # state plan S32 page and CMS (77 FR 17146-47) read it. The project
        # lead ruled on 2026-11-15 to follow the regulation where it
        # conflicts with 42 U.S.C. 1396a(k)(3), which reaches only a child
        # "who is eligible for medical assistance".
        has_uncovered_child = person.tax_unit.any(child_under_age & ~covered)
        return ~(is_caretaker & has_uncovered_child)
