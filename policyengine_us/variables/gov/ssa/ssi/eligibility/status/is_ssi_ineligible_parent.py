from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class is_ssi_ineligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible parent in respect of a child"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1160#d"

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        child = person("is_child", period)
        is_parent = person("is_parent", period)
        # 20 CFR 416.1160(d): an ineligible parent "is not eligible for SSI
        # benefits", which includes an aged, blind or disabled parent whose own
        # income, resources or noncitizen status rule out SSI. is_ssi_eligible has
        # no income test and, like ssi_countable_income and the marital income
        # variables, depends on this variable, so the parent's tests are read
        # from their own inputs.
        joint_claim = person("ssi_claim_is_joint", period)
        spouse_deeming = person("is_ssi_spousal_deeming_applies", period)
        as_couple = joint_claim | spouse_deeming
        earned = person("ssi_earned_income", period)
        unearned = person("ssi_unearned_income", period)
        countable_income = _apply_ssi_exclusions(
            where(as_couple, person.marital_unit.sum(earned), earned),
            where(as_couple, person.marital_unit.sum(unearned), unearned),
            parameters,
            period,
        )
        p = parameters(period).gov.ssa.ssi
        benefit_rate = where(as_couple, p.amount.couple, p.amount.individual)
        meets_income_test = countable_income <= benefit_rate * MONTHS_IN_YEAR
        resources = person("ssi_countable_resources", period)
        limit = p.eligibility.resources.limit
        # 20 CFR 416.1205(a) tests a married person against the couple limit,
        # including the resources of an ineligible spouse.
        meets_resource_test = where(
            person.marital_unit.nb_persons() == 2,
            person.marital_unit.sum(resources) <= limit.couple,
            resources <= limit.individual,
        )
        status = person("immigration_status", period)
        meets_noncitizen_test = (status == status.possible_values.CITIZEN) | person(
            "is_ssi_qualified_noncitizen", period
        )
        eligible_parent = (
            aged_blind_disabled
            & meets_income_test
            & meets_resource_test
            & meets_noncitizen_test
        )
        has_child_to_deem_to = person.tax_unit.sum(aged_blind_disabled & child) > 0
        return ~eligible_parent & ~child & is_parent & has_child_to_deem_to
