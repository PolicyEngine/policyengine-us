from policyengine_us.model_api import *


class cliff_evaluated(Variable):
    value_type = bool
    entity = Person
    label = "cliff evaluated"
    unit = USD
    documentation = "Whether this person's cliff has been simulated. If not, the cliff gap is assumed to be zero."
    definition_period = YEAR

    def formula(person, period, parameters):
        adult_index_values = person("adult_index", period)
        cliff_adult_count = parameters(period).simulation.cliff_adults
        is_adult = person("is_adult", period)
        return is_adult & (adult_index_values <= cliff_adult_count)


class cliff_gap(Variable):
    value_type = float
    entity = Person
    label = "cliff gap"
    unit = USD
    documentation = "Amount of income lost if this person's employment income increased by delta amount."
    definition_period = YEAR

    def formula(person, period, parameters):
        netinc_base = person.household("household_net_income", period)
        delta = parameters(period).simulation.cliff_delta
        adult_count = parameters(period).simulation.cliff_adults
        sim = person.simulation
        increase = np.zeros(person.count, dtype=np.float32)
        adult_indexes = person("adult_index", period)
        for adult_index in range(1, 1 + adult_count):
            alt_sim = sim.get_branch(f"cliff_for_adult_{adult_index}")
            for variable in sim.tax_benefit_system.variables:
                if (
                    variable not in sim.input_variables
                    or variable == "employment_income"
                ):
                    alt_sim.delete_arrays(variable)
            mask = adult_index == adult_indexes
            alt_sim.set_input(
                "employment_income",
                period,
                person("employment_income", period) + mask * delta,
            )
            alt_person = alt_sim.person
            netinc_alt = alt_person.household("household_net_income", period)
            increase[mask] += netinc_alt[mask] - netinc_base[mask]
            del sim.branches[f"cliff_for_adult_{adult_index}"]
        return where(increase < 0, -increase, 0)


class is_on_cliff(Variable):
    value_type = bool
    entity = Person
    label = "is on a tax-benefit cliff"
    documentation = "Whether this person would be worse off if their employment income were higher."
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("cliff_gap", period) > 0
