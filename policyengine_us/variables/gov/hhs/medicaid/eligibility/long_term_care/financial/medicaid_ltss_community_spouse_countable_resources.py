from policyengine_us.model_api import *


class medicaid_ltss_community_spouse_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS community spouse countable resources"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Delaware derives the community spouse's own current countable "
        "resources from the other person's resource inventory within their "
        "two-person marital unit. Supply each spouse's own "
        "medicaid_ltss_individual_countable_resources rather than a "
        "pre-attributed community-spouse total. Outside Delaware it reads "
        "medicaid_ltss_non_delaware_community_spouse_countable_resources, "
        "the spouse's own current comprehensive countable-resource "
        "inventory after applicable ownership and exclusion rules. Combined "
        "with applicant resources only for an initial "
        "eligibility determination. After the eligibility month in the same "
        "continuous LTSS period, these resources are not deemed available "
        "when medicaid_ltss_is_initial_eligibility_determination is false. "
        "Court orders, fair-hearing adjustments, and legal ownership "
        "determinations are not modeled."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396r-5"

    def formula_2026_01_01(person, period, parameters):
        state = person.household("state_code", period)
        own_resources = person("medicaid_ltss_individual_countable_resources", period)
        spouse_resources = person.marital_unit.sum(own_resources) - own_resources
        has_spouse = person("medicaid_ltss_has_community_spouse", period)
        delaware_resources = where(
            has_spouse & (person.marital_unit.nb_persons() == 2), spouse_resources, 0
        )
        return where(
            state == state.possible_values.DE,
            delaware_resources,
            person(
                "medicaid_ltss_non_delaware_community_spouse_countable_resources",
                period,
            ),
        )
