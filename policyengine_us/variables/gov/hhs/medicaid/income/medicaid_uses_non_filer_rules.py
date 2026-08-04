from policyengine_us.model_api import *


class medicaid_uses_non_filer_rules(Variable):
    value_type = bool
    entity = Person
    label = "Uses Medicaid MAGI non-filer household rules"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_3"

    def formula(person, period, parameters):
        is_tax_dependent = person("medicaid_is_tax_dependent", period)
        is_tax_filer = person.tax_unit("tax_unit_is_filer", period) & ~is_tax_dependent
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
            (~is_tax_filer & ~is_tax_dependent)
            | person("medicaid_uses_missing_claimant_fallback", period)
            | dependent_exception
        )
