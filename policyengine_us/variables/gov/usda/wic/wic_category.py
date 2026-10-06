from policyengine_us.model_api import *


class WICCategory(Enum):
    PREGNANT = "Pregnant"
    POSTPARTUM = "Postpartum"
    BREASTFEEDING = "Breastfeeding"
    INFANT = "Infant"
    CHILD = "Child"
    NONE = "None"


def _rank_mothers(person, entity, age, breastfeeding, eligible):
    # Rank the eligible mothers in each entity: breastfeeding mothers first,
    # then from youngest to oldest. Only use the rank together with eligible.
    breastfeeding_rank = person.get_rank(entity, age, eligible & breastfeeding)
    other_rank = person.get_rank(entity, age, eligible & ~breastfeeding)
    breastfeeding_mothers = entity.sum(eligible & breastfeeding)
    return where(breastfeeding, breastfeeding_rank, breastfeeding_mothers + other_rank)


class wic_category(Variable):
    value_type = Enum
    entity = Person
    definition_period = YEAR
    possible_values = WICCategory
    default_value = WICCategory.NONE
    documentation = "Demographic category for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "WIC demographic category"
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1786#b",
        "https://www.ecfr.gov/current/title-7/part-246/section-246.2",
    )

    def formula(person, period, parameters):
        pregnant = person("is_pregnant", period)
        mother = person("is_mother", period)
        breastfeeding = person("is_breastfeeding", period)
        age = person("age", period)
        tax_unit = person.tax_unit
        family = person.family
        # 7 CFR 246.2 defines postpartum and breastfeeding women by the time
        # since their own pregnancy (up to six months and one year), so an
        # infant makes only its mother postpartum or breastfeeding. Without
        # parent-child links, match each infant to one mother in its tax unit,
        # and an infant in a tax unit without a mother to one of the family's
        # remaining mothers, taking breastfeeding mothers first, then the
        # youngest.
        tax_unit_rank = _rank_mothers(person, tax_unit, age, breastfeeding, mother)
        tax_unit_has_mother = tax_unit.any(mother)

        def is_matched_to_infant_under(age_limit):
            infant = age < age_limit
            in_tax_unit = mother & (tax_unit_rank < tax_unit.sum(infant))
            unmatched_infants = family.sum(infant & ~tax_unit_has_mother)
            remaining = mother & ~in_tax_unit
            family_rank = _rank_mothers(person, family, age, breastfeeding, remaining)
            in_family = remaining & (family_rank < unmatched_infants)
            return in_tax_unit | in_family

        return select(
            [
                pregnant,
                breastfeeding & is_matched_to_infant_under(1),
                is_matched_to_infant_under(0.5),
                age < 1,
                age < 5,
            ],
            [
                WICCategory.PREGNANT,
                WICCategory.BREASTFEEDING,
                WICCategory.POSTPARTUM,
                WICCategory.INFANT,
                WICCategory.CHILD,
            ],
            default=WICCategory.NONE,
        )
