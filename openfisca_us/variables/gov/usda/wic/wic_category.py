from openfisca_us.model_api import *


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
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#b"

    def formula(person, period, parameters):
        pregnant = person("is_pregnant", period)
        mother = person("is_mother", period)
        breastfeeding = person("is_breastfeeding", period)
        age = person("age", period)
        # Categorize mothers based on the minimum age of children in the SPM unit.
        min_age_family = person.family.min(age)
        return select(
            *zip(
                (pregnant, WICCategory.PREGNANT),
                (
                    mother & breastfeeding & (min_age_family < 1),
                    WICCategory.BREASTFEEDING,
                ),
                (mother & (min_age_family < 0.5), WICCategory.POSTPARTUM),
                (age < 1, WICCategory.INFANT),
                (age < 5, WICCategory.CHILD),
                (True, WICCategory.NONE),
            )
        )
