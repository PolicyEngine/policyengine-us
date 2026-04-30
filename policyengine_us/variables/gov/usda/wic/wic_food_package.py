from policyengine_us.model_api import *


class WICFoodPackage(Enum):
    NONE = "NONE"
    PREGNANT_SINGLETON = "PREGNANT_SINGLETON"
    PREGNANT_MULTIPLE_FETUSES = "PREGNANT_MULTIPLE_FETUSES"
    PARTIALLY_BREASTFEEDING = "PARTIALLY_BREASTFEEDING"
    POSTPARTUM_NON_BREASTFEEDING = "POSTPARTUM_NON_BREASTFEEDING"
    FULLY_BREASTFEEDING = "FULLY_BREASTFEEDING"
    FULLY_BREASTFEEDING_MULTIPLES = "FULLY_BREASTFEEDING_MULTIPLES"
    INFANT_AVERAGE = "INFANT_AVERAGE"
    INFANT_0_3_FULLY_FORMULA_FED = "INFANT_0_3_FULLY_FORMULA_FED"
    INFANT_4_5_FULLY_FORMULA_FED = "INFANT_4_5_FULLY_FORMULA_FED"
    INFANT_0_3_PARTIALLY_BREASTFED = "INFANT_0_3_PARTIALLY_BREASTFED"
    INFANT_4_5_PARTIALLY_BREASTFED = "INFANT_4_5_PARTIALLY_BREASTFED"
    INFANT_6_11_PARTIALLY_BREASTFED = "INFANT_6_11_PARTIALLY_BREASTFED"
    INFANT_0_5_FULLY_BREASTFED = "INFANT_0_5_FULLY_BREASTFED"
    INFANT_6_11_FULLY_FORMULA_FED = "INFANT_6_11_FULLY_FORMULA_FED"
    INFANT_6_11_FULLY_BREASTFED = "INFANT_6_11_FULLY_BREASTFED"
    CHILD_12_23_MONTHS = "CHILD_12_23_MONTHS"
    CHILD_24_59_MONTHS = "CHILD_24_59_MONTHS"


class wic_food_package(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    possible_values = WICFoodPackage
    default_value = WICFoodPackage.NONE
    label = "WIC food package"
    documentation = "Federal WIC food package assigned to a participant"
    reference = "https://www.law.cornell.edu/cfr/text/7/246.10#e"

    def formula(person, period, parameters):
        wic_category = person("wic_category", period.this_year)
        category = wic_category.possible_values
        feeding_category = person("wic_infant_feeding_category", period)
        feeding = feeding_category.possible_values
        age = person("age", period.this_year)
        age_months = age * MONTHS_IN_YEAR
        current_pregnancies = person("current_pregnancies", period.this_year)
        is_breastfeeding = person("is_breastfeeding", period.this_year)
        fully_breastfeeding = person("is_wic_fully_breastfeeding", period)
        breastfeeding_infant_count = person("wic_breastfeeding_infant_count", period)

        pregnant = wic_category == category.PREGNANT
        infant = wic_category == category.INFANT
        child = wic_category == category.CHILD
        breastfeeding = wic_category == category.BREASTFEEDING
        postpartum = wic_category == category.POSTPARTUM

        average_infant = feeding_category == feeding.AVERAGE
        fully_formula_fed = feeding_category == feeding.FULLY_FORMULA_FED
        partially_breastfed = feeding_category == feeding.PARTIALLY_BREASTFED
        fully_breastfed = feeding_category == feeding.FULLY_BREASTFED

        return select(
            [
                pregnant & (current_pregnancies >= 2),
                pregnant & is_breastfeeding & (current_pregnancies == 1),
                pregnant,
                breastfeeding & fully_breastfeeding & (breastfeeding_infant_count >= 2),
                breastfeeding
                & (fully_breastfeeding | (breastfeeding_infant_count >= 2)),
                breastfeeding,
                postpartum,
                infant & average_infant,
                infant & (age_months < 4) & fully_formula_fed,
                infant & (age_months < 6) & fully_formula_fed,
                infant & (age_months < 4) & partially_breastfed,
                infant & (age_months < 6) & partially_breastfed,
                infant & partially_breastfed,
                infant & (age_months < 6) & fully_breastfed,
                infant & fully_formula_fed,
                infant & fully_breastfed,
                child & (age < 2),
                child,
            ],
            [
                WICFoodPackage.PREGNANT_MULTIPLE_FETUSES,
                WICFoodPackage.FULLY_BREASTFEEDING,
                WICFoodPackage.PREGNANT_SINGLETON,
                WICFoodPackage.FULLY_BREASTFEEDING_MULTIPLES,
                WICFoodPackage.FULLY_BREASTFEEDING,
                WICFoodPackage.PARTIALLY_BREASTFEEDING,
                WICFoodPackage.POSTPARTUM_NON_BREASTFEEDING,
                WICFoodPackage.INFANT_AVERAGE,
                WICFoodPackage.INFANT_0_3_FULLY_FORMULA_FED,
                WICFoodPackage.INFANT_4_5_FULLY_FORMULA_FED,
                WICFoodPackage.INFANT_0_3_PARTIALLY_BREASTFED,
                WICFoodPackage.INFANT_4_5_PARTIALLY_BREASTFED,
                WICFoodPackage.INFANT_6_11_PARTIALLY_BREASTFED,
                WICFoodPackage.INFANT_0_5_FULLY_BREASTFED,
                WICFoodPackage.INFANT_6_11_FULLY_FORMULA_FED,
                WICFoodPackage.INFANT_6_11_FULLY_BREASTFED,
                WICFoodPackage.CHILD_12_23_MONTHS,
                WICFoodPackage.CHILD_24_59_MONTHS,
            ],
            default=WICFoodPackage.NONE,
        )
