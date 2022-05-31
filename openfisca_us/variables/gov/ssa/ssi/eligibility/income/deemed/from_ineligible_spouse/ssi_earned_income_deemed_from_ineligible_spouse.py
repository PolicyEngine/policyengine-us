from openfisca_us.model_api import *


class ssi_earned_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        # First, determine unearned income from the ineligible spouse.
        # This is (a) in the law.
        ineligible_spouse = person("is_ssi_ineligible_spouse", period)
        unearned_income = person("ssi_unearned_income", period)
        marital_unit = person.marital_unit
        ineligible_spousal_unearned_income = (
            marital_unit.sum(ineligible_spouse * unearned_income)
            - ineligible_spouse * unearned_income
        )
        earned_income = person("ssi_earned_income", period)
        ineligible_spousal_earned_income = (
            marital_unit.sum(ineligible_spouse * earned_income)
            - ineligible_spouse * earned_income
        )

        # Next, (b) determine and subtract allocations for ineligible children.
        child_allocations = add(
            person.tax_unit, period, ["ssi_ineligible_child_allocation"]
        ) * person("is_ssi_aged_blind_disabled", period)
        # Child allocations are deducted from unearned income first - ensure we only deduct
        # the remaining allocations from earned income.
        remaining_child_allocations = max_(
            0, child_allocations - ineligible_spousal_unearned_income
        )
        return max_(
            0, ineligible_spousal_earned_income - remaining_child_allocations
        )
