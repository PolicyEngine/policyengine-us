from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed.ssi_resources_deemed_from_ineligible_parent import (
    _ssi_parental_resource_pool,
)


class ia_ssa_resources_deemed_from_parents(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA resources deemed from parents"
    definition_period = MONTH
    quantity_type = STOCK
    unit = USD
    defined_for = StateCode.IA
    reference = (
        # PDF pages 9, 12, 46-47
        "https://hhs.iowa.gov/media/3987/download?inline=#page=9",
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1856",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330200",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330280",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330310",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330340",
    )
    # 6-B deems parental resources above the $2,000 one-parent or $3,000
    # two-parent allowance "in the same manner as SSI policy"; these equal the
    # SSI limits, so the federal parameters are used. The deemors are
    # the co-resident parents named by parent links (or the unlinked-parent
    # proxy) plus each parent's co-resident spouse, as in SSI's
    # 416.1202(b)(1) pool, so a stepparent's resources are deemed. Parents
    # receiving SSI are not resource deemors, but the allowance follows the
    # number of co-resident deemors including them. The excess is divided
    # among the children of the same deemors who receive SSI or would
    # otherwise receive in-home health-related care, removing any child whose
    # own resources plus the share exceed the limit (SI 01330.200 and .280).
    # 6-B p.9: "For an SSI recipient, accept the Social Security
    # Administration's determination of SSI eligibility as verification that
    # income, resources, and age, blindness or disability requirements have
    # been met." The child test is is_ssi_resource_deeming_child, which
    # applies SSA's exclusions (the 416.1202(b)(2) home-care exception, a
    # medical treatment facility, a married or household-head minor). Iowa
    # therefore deems only where SSA would, and in-home care children are
    # deemed "in the same manner as SSI policy" (6-B p.46; ia_ssa.yaml Cases 80
    # and 83). Other state-only sibling eligibility is not modeled.

    def formula(person, period, parameters):
        limit = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        resources = where(receives_ssi, 0, person("ssi_resources_for_deeming", period))
        parental_resources, parent_count, pool = _ssi_parental_resource_pool(
            person, period, resources
        )
        allowance = where(parent_count > 1, limit.couple, limit.individual)
        excess = max_(parental_resources - allowance, 0)
        child = person("is_ssi_resource_deeming_child", period)
        ihhrc = person("ia_ssa_nonfinancial_eligible", period) & (
            person("ia_ssa_ihhrc_amount", period) > 0
        )
        own = person("ssi_countable_resources", period.this_year)
        eligible = child & (receives_ssi | ihhrc) & (own <= limit.individual)
        pool_count = int(np.max(pool, initial=-1)) + 1
        share = excess
        # Each round removes at least one child or leaves the result stable.
        for _ in range(int(np.max(person.household.nb_persons(), initial=0)) + 1):
            count = np.bincount(pool[eligible], minlength=pool_count)
            share = excess / max_(count[pool], 1)
            remaining = eligible & (own + share <= limit.individual)
            if np.array_equal(remaining, eligible):
                break
            eligible = remaining
        return child * share
