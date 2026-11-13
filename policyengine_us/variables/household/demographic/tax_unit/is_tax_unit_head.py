from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit._head_or_spouse_candidates import (
    head_or_spouse_candidates,
)


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6013",
        "https://www.law.cornell.edu/uscode/text/26/152",
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # A dataset's tax-unit constructor can supply every member's role.
        role = person("tax_unit_role_input", period)
        supplied = tax_unit("tax_unit_roles_supplied", period)
        # Otherwise the oldest adult is the head, skipping input dependents.
        eligible = head_or_spouse_candidates(person, period)
        # A married couple can file a joint return (26 USC 6013(a)), and a
        # couple who files a joint return can't be claimed as anyone's
        # dependents (26 USC 152(b)(2)). So when two such adults share a
        # two-person marital unit within this tax unit, the older of the
        # couple heads it, even if another adult is older. When a situation
        # omits marital units, Core puts everyone in one unit, so this changes
        # nothing there: a two-person unit gives the same head.
        # A separated member doesn't form such a couple: is_tax_unit_spouse
        # gives no one the spouse role in a unit with a separated member.
        # NOTE: the older adult then becomes the couple's dependent whatever
        # their income. If that adult files instead, claiming a couple who
        # don't file jointly, supply is_tax_unit_head or tax_unit_role_input.
        marital_unit = person.marital_unit
        tax_unit_id = tax_unit.reference_entity.members_entity_id
        couple_eligible = eligible & ~person("is_separated", period)
        couple_candidate = (
            couple_eligible
            & (marital_unit.nb_persons() == 2)
            & (marital_unit.sum(couple_eligible) == 2)
            & (marital_unit.min(tax_unit_id) == marital_unit.max(tax_unit_id))
        )
        eligible = where(tax_unit.any(couple_candidate), couple_candidate, eligible)
        age = person("age", period)
        oldest_candidate = person.get_rank(tax_unit, -age, eligible) == 0
        return where(supplied, role == role.possible_values.HEAD, oldest_candidate)
