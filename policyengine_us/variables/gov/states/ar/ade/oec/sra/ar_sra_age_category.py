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
    reference = "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.rates.age_category_months
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return p.calc(age_months)
