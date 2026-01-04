from policyengine_us.model_api import *


class AKATAPUnitType(Enum):
    """Alaska ATAP assistance unit types per 7 AAC 45.520 and State Plan."""

    CHILD_ONLY = "Child only"
    PREGNANT_WOMAN = "Pregnant woman"
    ONE_PARENT = "One parent"
    TWO_PARENT_ABLE = "Two parent able"
    TWO_PARENT_INCAPACITATED = "Two parent incapacitated"


class ak_atap_unit_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = AKATAPUnitType
    default_value = AKATAPUnitType.ONE_PARENT
    label = "Alaska ATAP assistance unit type"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Basic demographic checks
        is_child = person("is_child", period.this_year)
        is_pregnant = person("is_pregnant", period.this_year)
        is_disabled = person("is_disabled", period.this_year)

        # Unit composition counts
        has_children = spm_unit.any(is_child)
        all_children = spm_unit.all(is_child)
        num_adults = spm_unit.sum(~is_child)

        # Pregnant woman only: pregnant with no children
        has_pregnant_woman = spm_unit.any(is_pregnant)
        is_pregnant_woman_only = has_pregnant_woman & ~has_children

        # Child-only: all members are children
        is_child_only = has_children & all_children

        # Two-parent: 2+ adults with children
        is_two_parent = has_children & (num_adults >= 2)

        # Incapacitated: two-parent with one disabled and one able adult
        is_disabled_adult = ~is_child & is_disabled
        has_disabled_adult = spm_unit.any(is_disabled_adult)
        is_able_adult = ~is_child & ~is_disabled
        has_able_adult = spm_unit.any(is_able_adult)
        is_incapacitated = is_two_parent & has_disabled_adult & has_able_adult

        # Two-parent able: two-parent but not incapacitated
        is_two_parent_able = is_two_parent & ~is_incapacitated

        return select(
            [
                is_pregnant_woman_only,
                is_child_only,
                is_incapacitated,
                is_two_parent_able,
            ],
            [
                AKATAPUnitType.PREGNANT_WOMAN,
                AKATAPUnitType.CHILD_ONLY,
                AKATAPUnitType.TWO_PARENT_INCAPACITATED,
                AKATAPUnitType.TWO_PARENT_ABLE,
            ],
            default=AKATAPUnitType.ONE_PARENT,
        )
