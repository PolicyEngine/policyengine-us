from policyengine_us.model_api import *


class mi_home_heating_credit_eligible_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the Michigan home heating credit"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        tax_unit_size = tax_unit("tax_unit_size", period)
        person = tax_unit.members
        dependent_elsewhere = person(
            "claimed_as_dependent_on_another_return", period
        )
        ft_student = person("is_full_time_student", period)

        eligible_person = ~(ft_student & dependent_elsewhere)
        eligible_people = tax_unit.sum(eligible_person)
        # The heating credit is prorated based on the number of eligible people
        # in the tax unit.
        prorate_fraction = np.zeros_like(eligible_people)
        mask = eligible_people > 0
        prorate_fraction[mask] = eligible_people[mask] / tax_unit_size[mask]
        return prorate_fraction
