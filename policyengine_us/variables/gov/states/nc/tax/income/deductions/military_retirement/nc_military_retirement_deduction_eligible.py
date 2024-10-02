from policyengine_us.model_api import *


class nc_military_retirement_deduction_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina military retirement deduction eligible"
    definition_period = YEAR
    defined_for = StateCode.NC
    reference = (
        "https://www.ncdor.gov/2022-d-401-individual-income-tax-instructions/open#page=18",
        "https://law.justia.com/codes/north-carolina/chapter-105/article-4/section-105-153-5/",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.nc.tax.income.deductions.military_retirement
        is_medically_retired = person(
            "is_permanently_disabled_veteran", period
        )
        served_minimum_years = (
            person("years_in_military", period) >= p.minimum_years
        )
        return is_medically_retired | served_minimum_years
