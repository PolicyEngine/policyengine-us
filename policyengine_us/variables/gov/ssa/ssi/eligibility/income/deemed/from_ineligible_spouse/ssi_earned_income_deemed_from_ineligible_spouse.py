from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_earned_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        # First, determine unearned income from the ineligible spouse.
        # This is (a) in the law. The spouse is the co-resident husband or
        # wife (416.1160(d)), whatever their tax-unit role.
        spouse = _ssi_spouse_index(person, period)
        safe_spouse = np.maximum(spouse, 0)
        has_ineligible_spouse = (spouse >= 0) & person(
            "is_ssi_ineligible_spouse", period
        )[safe_spouse]
        unearned_income = person("ssi_unearned_income", period)
        ineligible_spousal_unearned_income = where(
            has_ineligible_spouse, unearned_income[safe_spouse], 0
        )
        earned_income = person("ssi_earned_income", period)
        ineligible_spousal_earned_income = where(
            has_ineligible_spouse, earned_income[safe_spouse], 0
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
        return max_(0, ineligible_spousal_earned_income - remaining_child_allocations)
