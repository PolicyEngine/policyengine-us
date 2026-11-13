from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_established_spouse_indices,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status._ssi_parent_supplement import (
    _ssi_parent_supplement_level,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    is_parent_of_any,
)


class is_ssi_ineligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible parent in respect of a child"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1160#d",
        "https://www.law.cornell.edu/cfr/text/20/416.1163#d",
        "https://www.law.cornell.edu/cfr/text/20/416.1161#a_2",
        "https://www.law.cornell.edu/cfr/text/20/416.1166",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320620",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320630",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058",
    )

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        child = person("is_child", period)
        # 20 CFR 416.1160(d): an ineligible parent "is not eligible for SSI
        # benefits", which includes an aged, blind or disabled parent whose own
        # income, resources or noncitizen status rule out SSI. is_ssi_eligible has
        # no income test and, like ssi_countable_income and the marital income
        # variables, depends on this variable, so the parent's tests are read
        # from their own inputs.
        joint_claim = person("ssi_claim_is_joint", period)
        earned = person("ssi_earned_income", period)
        unearned = person("ssi_unearned_income", period)
        # A joint claim tests the couple's income. Otherwise 416.1163(d)(2) adds
        # what remains of an ineligible spouse's income after the allocations
        # for ineligible children in 416.1163(b).
        countable_income = _apply_ssi_exclusions(
            where(joint_claim, person.marital_unit.sum(earned), earned),
            where(joint_claim, person.marital_unit.sum(unearned), unearned),
            parameters,
            period,
        ) + person("ssi_income_deemed_from_ineligible_spouse", period)
        p = parameters(period).gov.ssa.ssi
        benefit_rate = where(
            joint_claim | person("is_ssi_spousal_deeming_applies", period),
            p.amount.couple,
            p.amount.individual,
        )
        # 20 CFR 416.1166 counts a federally administered State supplement as an
        # SSI benefit, and 416.1161(a)(2) leaves out of deeming the income of a
        # parent who receives one (POMS SI 01320.620 B.6 and C.3). So the test
        # adds the state's at-home supplement where SSA pays one to the parent.
        meets_income_test = countable_income <= (
            benefit_rate * MONTHS_IN_YEAR
            + _ssi_parent_supplement_level(person, period, parameters)
        )
        resources = person("ssi_countable_resources", period)
        limit = p.eligibility.resources.limit
        first, second = co_resident_parent_indices(person, period)
        spouse = _ssi_established_spouse_indices(person, period, first, second)
        # 20 CFR 416.1205(a) tests a married person against the couple limit,
        # including the resources of an ineligible spouse.
        meets_resource_test = where(
            spouse >= 0,
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
        # 416.1160(d) limits an ineligible parent to a natural or adoptive parent
        # who lives with the child, or that parent's spouse, wherever the spouse
        # files, as on the resource side (ssi_resources_deemed_from_ineligible_parent).
        # Parent ids settle who the parents are. With no ids, the tax-unit proxy
        # cannot tell a grandparent or an unrelated parent from the child's parent:
        # this is a data limitation.
        eligible_child = aged_blind_disabled & child
        has_own_child = is_parent_of_any(person, period, eligible_child)
        spouse_of_parent = (spouse >= 0) & has_own_child[np.maximum(spouse, 0)]
        return ~eligible_parent & ~child & (has_own_child | spouse_of_parent)
