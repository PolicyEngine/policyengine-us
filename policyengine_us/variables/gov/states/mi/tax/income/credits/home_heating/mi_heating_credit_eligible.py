from policyengine_us.model_api import *


class mi_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible Household for the Michigan heating credit"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_not_dependent_elsewhere = ~tax_unit("spouse_is_dependent_elsewhere", period)
        spouse_not_dependent_elsewhere = ~tax_unit("spouse_is_dependent_elsewhere", period)
        is_not_ft_student = ~person("is_full_time_student", period)

        student_eligible = tax_unit.any(is_not_ft_student) & (head_not_dependent_elsewhere | spouse_not_dependent_elsewhere)

        # Tax units can not have household resources greater than 110% of the poverty guidelines
        household_resources = tax_unit("mi_household_resources", period)
        fpg = tax_unit("tax_unit_fpg", period)
        p = parameters(period).gov.states.mi.tax.income.credits.home_heating
        resource_eligible = household_resources < fpg * p.fpg_rate
        return student_eligible & resource_eligible
