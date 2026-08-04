from policyengine_us.model_api import *


class ArSraAgeCategory(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGED = "School-Aged"


class ar_sra_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = ArSraAgeCategory
    default_value = ArSraAgeCategory.INFANT
    definition_period = MONTH
    defined_for = StateCode.AR
    label = "Arkansas SRA child age category"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Part_Time_20251101_OEC.pdf",
        "https://law.justia.com/codes/arkansas/title-6/subtitle-2/chapter-18/subchapter-2/section-6-18-207/",
    )

    def formula(person, period, parameters):
        # Infant/Toddler boundaries follow AR Min Licensing (DCCECE 2020).
        # The 72-month School-Aged boundary tracks typical kindergarten entry
        # under Ark. Code §6-18-207 (age 5 by Aug 1 of the school year);
        # Preschool spans the 36-71 month gap.
        p = parameters(period).gov.states.ar.ade.oec.sra.rates.age_category_months
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return p.calc(age_months)
