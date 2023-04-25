from policyengine_us.model_api import *


class cliff_evaluated(Variable):
    value_type = bool
    entity = Person
    label = "cliff evaluated"
    unit = USD
    documentation = "Whether this person's cliff has been simulated. If not, then the cliff gap is assumed to be zero."
    definition_period = YEAR

    def formula(person, period, parameters):
        adult_index_values = person("adult_index", period)
        cliff_adult_count = parameters(period).simulation.cliff_adults
        return adult_index_values <= cliff_adult_count


class cliff_gap(Variable):
    value_type = float
    entity = Person
    label = "cliff gap"
    unit = USD
    documentation = "Amount of income lost if this person's employment income increased by $2,000."
    definition_period = YEAR

    def formula(person, period, parameters):
        simulation = person.simulation
        alt_simulation = simulation.get_branch(f"all_adults_2k_pay_rise")
        delta = parameters(period).simulation.cliff_threshold
        for variable in simulation.tax_benefit_system.variables:
            if variable not in simulation.input_variables:
                alt_simulation.delete_arrays(variable)
        alt_simulation.set_input(
            "employment_income",
            period,
            person("employment_income", period)
            + person("is_adult", period) * delta,
        )
        alt_person = alt_simulation.person
        household_net_income = person.spm_unit("spm_unit_net_income", period)
        household_net_income_higher_earnings = alt_person.spm_unit(
            "spm_unit_net_income", period
        )
        increase = household_net_income_higher_earnings - household_net_income
        return where(person("is_adult", period) & (increase < 0), -increase, 0)


class is_on_cliff(Variable):
    value_type = bool
    entity = Person
    label = "is on a tax-benefit cliff"
    documentation = "Whether this person would be worse off if their employment income were $2,000 higher."
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("cliff_gap", period) > 0
