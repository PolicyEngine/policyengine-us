from policyengine_us.model_api import *


class medicaid_home_equity_limit_family_exception(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid home equity limit family exception"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f_2"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care
        receives_long_term_care = person(
            "receives_medicaid_long_term_care_services", period
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_resident_spouse = person.marital_unit.nb_persons() == 2
        # The model does not have pairwise parent-child identifiers.
        # Treat related household members as the resident child proxy.
        qualifying_resident_child = person("is_related_to_head_or_spouse", period) & (
            (person("age", period) < p.home_equity.family_exception.child_age_threshold)
            | person("is_blind", period)
            | person("is_disabled", period)
            | person("is_permanently_and_totally_disabled", period)
        )
        has_resident_child = (
            person.household.sum(qualifying_resident_child) > qualifying_resident_child
        )
        return receives_long_term_care & (
            has_resident_spouse | (is_head_or_spouse & has_resident_child)
        )
