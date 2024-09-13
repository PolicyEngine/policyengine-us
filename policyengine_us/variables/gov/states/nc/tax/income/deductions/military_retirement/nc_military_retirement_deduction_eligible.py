from policyengine_us.model_api import *


class nc_military_retirement_deduction_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina military retirement deduction eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.nc.tax.income.deductions.military_retirement
        is_medically_retired = person("is_medically_retired", period)
        served_minimum_years = (
            person("years_in_military", period) >= p.minimum_years
        )
        return is_medically_retired | served_minimum_years
