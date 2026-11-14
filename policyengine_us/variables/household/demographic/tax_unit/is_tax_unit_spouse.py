from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit._head_or_spouse_candidates import (
    head_or_spouse_candidates,
)


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/152#c_3",
        "https://www.law.cornell.edu/uscode/text/26/7703#a_2",
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # A dataset's tax-unit constructor can supply every member's role.
        role = person("tax_unit_role_input", period)
        supplied = tax_unit("tax_unit_roles_supplied", period)
        # Otherwise only non-head adults can be spouses, skipping input
        # dependents.
        candidate = head_or_spouse_candidates(person, period)
        head = person("is_tax_unit_head", period)
        eligible = candidate & ~head
        # A marital unit holds a married, cohabiting couple, and
        # is_tax_unit_head takes the head from such a couple when the tax
        # unit has one, so the head's partner in their marital unit is the
        # spouse. A head without one takes the next-oldest adult, except an
        # adult who meets the qualifying child age test against the head:
        # under 19, or under 24 if a full-time student, and younger than
        # the head, or permanently and totally disabled (26 USC 152(c)(3)).
        # That adult can be the head's dependent, so an adult child isn't
        # paired with their parent, while an older adult's income stays on
        # the return. When a situation omits marital units, Core puts
        # everyone in one unit, so the age order applies unchanged. Compare
        # memberships, not the ID variable: situations can supply groups
        # without numeric ID inputs.
        # NOTE: an adult outside the head's marital unit who fails the age
        # test is still paired with the head, even if they could be a
        # qualifying relative. A permanently and totally disabled adult
        # outside the head's marital unit becomes a dependent whatever their
        # income. Supply is_tax_unit_spouse or tax_unit_role_input for these
        # households.
        marital_unit = person.marital_unit.reference_entity.members_entity_id
        head_marital_unit = tax_unit.max(where(head, marital_unit, -1))
        in_head_marital_unit = marital_unit == head_marital_unit
        age = person("age", period)
        p = parameters(period).gov.irs.dependent.ineligible_age
        student = person("is_full_time_student", period)
        age_limit = where(student, p.student, p.non_student)
        head_age = tax_unit.max(where(head, age, 0))
        meets_age_test = ((age < age_limit) & (age < head_age)) | person(
            "is_permanently_and_totally_disabled", period
        )
        has_partner = tax_unit.any(eligible & in_head_marital_unit)
        eligible = where(
            has_partner,
            eligible & in_head_marital_unit,
            eligible & ~meets_age_test,
        )
        next_oldest_adult = person.get_rank(tax_unit, -age, eligible) == 0
        # Legal separation concerns the head's own marriage (26 USC 7703).
        # Select before checking separation, without promoting another adult;
        # member order breaks equal-age ties.
        separated = person("is_separated", period)
        head_or_spouse_separated = tax_unit.any((head | next_oldest_adult) & separated)
        next_oldest_adult = next_oldest_adult & ~head_or_spouse_separated
        # An explicit is_tax_unit_head input still wins over a supplied role,
        # so keep the head out of the spouse role either way.
        supplied_spouse = (role == role.possible_values.SPOUSE) & ~head
        return where(supplied, supplied_spouse, next_oldest_adult)
