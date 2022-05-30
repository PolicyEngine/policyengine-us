from openfisca_us.model_api import *
from openfisca_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ssi_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

    def formula(person, period, parameters):
        eligible_child = person("is_ssi_aged_blind_disabled", period) & person(
            "is_child", period
        )
        ineligible_parent = person("is_ssi_ineligible_parent", period)

        ineligible_parents_income = eligible_child * _apply_ssi_exclusions(
            eligible_child
            * person.tax_unit.sum(
                person("ssi_earned_income", period) * ineligible_parent
            ),
            eligible_child
            * person.tax_unit.sum(
                person("ssi_unearned_income", period) * ineligible_parent
            ),
            parameters,
            period,
        )

        child_allocations = add(
            person.tax_unit, period, ["ssi_ineligible_child_allocation"]
        )
        parental_allocations = add(
            person.tax_unit, period, ["ssi_ineligible_parent_allocation"]
        )
        total_allocations = child_allocations + parental_allocations

        net_parental_deemed_income = max_(
            0, ineligible_parents_income - total_allocations
        )
        num_eligible_children = person.tax_unit.sum(eligible_child)
        return where(
            num_eligible_children > 0,
            net_parental_deemed_income / num_eligible_children,
            0,
        )
