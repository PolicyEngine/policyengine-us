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
        DELTA = 2_000
        cliff_values = np.zeros(person.count, dtype=np.float32)
        simulation = person.simulation
        adult_index_values = person("adult_index", period)
        cliff_adult_count = parameters(period).simulation.cliff_adults
        for adult_index in range(1, 1 + cliff_adult_count):
            alt_simulation = simulation.get_branch(f"adult_{adult_index}_2k_pay_rise")
            mask = adult_index_values == adult_index
            for variable in simulation.tax_benefit_system.variables:
                if variable not in simulation.input_variables:
                    alt_simulation.delete_arrays(variable)
            alt_simulation.set_input(
                "employment_income", period, 
                person("employment_income", period)
                + mask * DELTA,
            )
            alt_person = alt_simulation.person
            household_net_income = person.household("household_net_income", period)
            household_net_income_higher_earnings = alt_person.household(
                "household_net_income", period
            )
            increase = household_net_income_higher_earnings - household_net_income
            cliff_values += where(mask & (increase < 0), -increase, 0)
        return cliff_values

class is_on_cliff(Variable):
    value_type = bool
    entity = Person
    label = "is on a tax-benefit cliff"
    documentation = "Whether this person would be worse off if their employment income were $2,000 higher."
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("cliff_gap", period) > 0