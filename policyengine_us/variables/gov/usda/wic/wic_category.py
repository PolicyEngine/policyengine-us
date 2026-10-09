from policyengine_us.model_api import *


class WICCategory(Enum):
    PREGNANT = "Pregnant"
    POSTPARTUM = "Postpartum"
    BREASTFEEDING = "Breastfeeding"
    INFANT = "Infant"
    CHILD = "Child"
    NONE = "None"


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
        # parent-child links, match each infant to at most one woman.
        infant = age < 1
        young_infant = age < 0.5
        in_motherless_tax_unit = ~tax_unit.any(mother)

        # 1. A woman reported as breastfeeding is feeding an infant, so match
        # her first: to an infant in her tax unit, else to any remaining infant
        # in her family (youngest breastfeeding women first).
        bf_rank_tax_unit = person.get_rank(tax_unit, age, breastfeeding)
        bf_in_tax_unit = breastfeeding & (bf_rank_tax_unit < tax_unit.sum(infant))
        bf_rest = breastfeeding & ~bf_in_tax_unit
        bf_rank_family = person.get_rank(family, age, bf_rest)
        family_infants_left = family.sum(infant) - family.sum(bf_in_tax_unit)
        bf_in_family = bf_rest & (bf_rank_family < family_infants_left)
        breastfeeding_woman = bf_in_tax_unit | bf_in_family

        # Take the matched infants out of the pools, oldest first, so that
        # breastfeeding women count against infants aged six months to one
        # year before younger ones (inputs cannot tell which infant is whose:
        # a breastfeeding woman and another mother in one tax unit are assumed
        # to have the older and the younger infant). Family matches take
        # infants from tax units without a mother first.
        infant_rank_tax_unit = person.get_rank(tax_unit, -age, infant)
        taken = infant & (infant_rank_tax_unit < tax_unit.sum(bf_in_tax_unit))
        left = infant & ~taken
        infant_rank_family = person.get_rank(
            family, where(in_motherless_tax_unit, 0, 2) - age, left
        )
        taken = taken | (left & (infant_rank_family < family.sum(bf_in_family)))
        free_young_infant = young_infant & ~taken

        # 2. Match each remaining infant under six months to one other mother
        # in its tax unit, youngest first, and an infant in a tax unit without
        # a mother to one of the family's remaining mothers.
        candidate = mother & ~breastfeeding_woman
        pp_rank_tax_unit = person.get_rank(tax_unit, age, candidate)
        pp_in_tax_unit = candidate & (
            pp_rank_tax_unit < tax_unit.sum(free_young_infant)
        )
        pp_rest = candidate & ~pp_in_tax_unit
        pp_rank_family = person.get_rank(family, age, pp_rest)
        pp_in_family = pp_rest & (
            pp_rank_family < family.sum(free_young_infant & in_motherless_tax_unit)
        )
        postpartum = pp_in_tax_unit | pp_in_family

        return select(
            [
                pregnant,
                breastfeeding_woman,
                postpartum,
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
