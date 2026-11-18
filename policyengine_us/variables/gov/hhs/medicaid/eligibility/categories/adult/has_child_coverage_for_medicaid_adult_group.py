from policyengine_us.model_api import *


class has_child_coverage_for_medicaid_adult_group(Variable):
    value_type = bool
    entity = Person
    label = "Has coverage that satisfies the Medicaid adult group child coverage requirement"
    documentation = (
        "Whether the person, as a child, has Medicaid, Children's Health "
        "Insurance Program, Marketplace or other minimum essential coverage "
        "for a parent's or caretaker relative's eligibility for the Medicaid "
        "adult group (42 CFR 435.119(c)). Modeled Medicaid and CHIP count "
        "when the person is eligible and takes up; modeled Marketplace "
        "coverage counts when the person can enroll and the tax unit takes "
        "up; reported coverage inputs count as listed."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.119#c_1",
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/NJ/NJ-13-0011-MM1.pdf#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.adult.child_coverage
        listed_coverage = add(person, period, p.qualifying_coverage) > 0
        # is_aca_marketplace_enrollee includes a fourth or later child, who is
        # enrolled but pays no age-rated premium, unlike person_receives_aca.
        marketplace = person("is_aca_marketplace_enrollee", period) & person.tax_unit(
            "takes_up_aca_if_eligible", period
        )
        return listed_coverage | marketplace
