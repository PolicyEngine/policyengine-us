from policyengine_us.model_api import *


class medicaid_uses_missing_claimant_fallback(Variable):
    value_type = bool
    entity = Person
    label = "Uses Medicaid MAGI missing-claimant non-filer fallback"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2"

    def formula(person, period, parameters):
        claimed_by_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        dependent_exception = (
            person(
                "medicaid_tax_dependent_exception_other_than_spouse_or_child",
                period,
            )
            | person(
                "medicaid_tax_dependent_exception_living_with_both_parents",
                period,
            )
            | person(
                "medicaid_tax_dependent_exception_non_custodial_parent",
                period,
            )
        )

        return (
            claimed_by_another_return
            & ~person("medicaid_has_known_claiming_tax_unit", period)
            & ~dependent_exception
        )
