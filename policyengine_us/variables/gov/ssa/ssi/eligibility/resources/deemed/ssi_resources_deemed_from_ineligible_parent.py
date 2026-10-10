from policyengine_us.model_api import *


def _sum_coresident_tax_unit(person, values, temporary):
    """Sum over the intersection of a tax unit and an actual household.

    Keep the same tax-unit family proxy as SSI income deeming. A tax unit
    must contain only the child's natural/adoptive parents and their spouses
    as parental participants; is_parent alone cannot identify which child's
    parent an unrelated adult is. Separate tax units need explicit inputs
    for their deemed amounts. No optional parent-link APIs are required.
    """
    group = person.tax_unit
    indices = np.arange(person.count)
    households = person.household.reference_entity.members_entity_id
    total = np.zeros(person.count)
    for position in range(int(np.max(group.reference_entity.members_position)) + 1):
        member = group.value_nth_person(position, indices, default=-1)
        # 416.1167: an adjudicated temporary absence retains membership in
        # the SSI household represented by this tax unit, including a medical
        # facility absence while benefits under 416.212 remain payable.
        coresident = (member >= 0) & (
            (households[member] == households) | temporary[member] | temporary
        )
        total += where(coresident, values[member], 0)
    return total


class ssi_resources_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI resources deemed from ineligible parents"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1205",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330200",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330280",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330310",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330340",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        parent = person("is_parent", period)
        # 416.1202(b)(1): the parent's spouse is a stepparent living with
        # the child and parent. A marital-unit spouse need not have own children.
        parent = parent | person.marital_unit.any(parent)
        temporary = person("ssi_resource_deeming_temporary_absence", period)
        parental_resources = _sum_coresident_tax_unit(
            person, parent * person("ssi_resources_for_deeming", period), temporary
        )
        parent_count = _sum_coresident_tax_unit(person, parent, temporary)
        # 'only to the extent that those resources exceed the resource limits
        # described in § 416.1205': use the reformable individual/couple limits.
        allowance = where(parent_count > 1, p.couple, p.individual)
        excess = max_(0, parental_resources - allowance)
        # Do not discard ABD parents. SI 01330.310 B-C says zero if parent(s)
        # meets resource eligibility, usual deeming if not. The Ryder example
        # (.340) has an ABD mother failing the couple limit: 3100-3000=100.
        own_resources = person("ssi_countable_resources", period)
        active = person("is_ssi_resource_deeming_child", period) & (
            own_resources <= p.individual
        )
        deemed = np.zeros(person.count)
        # SI 01330.200 B: 'equally divide' among eligible children; when a
        # child is ineligible 'divide ... among the remaining eligible children'.
        # Retain the last tested share for a failed child, then redistribute.
        # Each round removes at least one child or leaves the result stable;
        # at most the largest tax-unit size rounds are needed (Goode, .280).
        rounds = int(np.max(person.tax_unit.nb_persons()))
        for _ in range(rounds):
            count = _sum_coresident_tax_unit(person, active, temporary)
            share = excess / max_(1, count)
            deemed = where(active, share, deemed)
            active = active & (own_resources + share <= p.individual)
        return deemed
