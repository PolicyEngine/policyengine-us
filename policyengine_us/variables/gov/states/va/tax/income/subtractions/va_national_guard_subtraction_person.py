from policyengine_us.model_api import *


class va_national_guard_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia National Guard pay subtraction allocated to each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        # The subtraction caps the household's military service income, so
        # allocate the capped tax-unit amount by each person's share.
        total = person.tax_unit("va_national_guard_subtraction", period)
        military_service_income = person("military_service_income", period)
        total_military_service_income = person.tax_unit.sum(military_service_income)
        share = where(
            total_military_service_income > 0,
            military_service_income / total_military_service_income,
            0,
        )
        return total * share
