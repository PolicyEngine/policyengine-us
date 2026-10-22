from policyengine_us.model_api import *


class is_in_medicaid_medically_needy_category(Variable):
    value_type = bool
    entity = Person
    label = "In Medicaid medically needy category"
    documentation = "Whether this person is in a Medicaid category for which there is a medically needy pathway."
    definition_period = YEAR
    reference = "https://www.ndlegis.gov/information/acdata/pdf/75-02-02.1.pdf#page=11"

    def formula(person, period, parameters):
        mn_categories = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.medically_needy.categories
        aged_threshold = parameters(period).gov.ssa.ssi.eligibility.aged_threshold
        is_child = any_(person, period, mn_categories.child.child_categories)
        state = person.household("state_code_str", period)
        # N.D.A.C. 75-02-02.1-05(3)(e) also covers blind individuals.
        is_disabled = person("is_ssi_disabled", period) | (
            (state == "ND") & person("is_blind", period)
        )
        is_senior = person("age", period) >= aged_threshold
        is_pregnant = person("is_pregnant_for_medicaid_nfc", period)
        is_parent = person("is_parent_for_medicaid_nfc", period)
        mn = mn_categories
        categories = [
            mn.child.child,
            mn.disabled,
            mn.parent,
            mn.pregnant,
            mn.senior,
        ]
        category_covered = [parameter[state] > 0 for parameter in categories]
        in_category = [
            is_child,
            is_disabled,
            is_parent,
            is_pregnant,
            is_senior,
        ]
        return np.logical_or.reduce(
            [
                person_in_category & category_is_covered
                for person_in_category, category_is_covered in zip(
                    in_category, category_covered
                )
            ]
        )
