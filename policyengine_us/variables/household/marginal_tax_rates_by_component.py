from policyengine_us.model_api import *


class federal_marginal_tax_rate(Variable):
    label = "federal marginal tax rate"
    documentation = (
        "Marginal change in federal income tax per dollar of additional earnings."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        base_tax = person.tax_unit("income_tax", period)
        delta = parameters(period).simulation.marginal_tax_rate_delta
        adult_count = parameters(period).simulation.marginal_tax_rate_adults
        sim = person.simulation
        mtr_values = np.zeros(person.count, dtype=np.float32)
        adult_indexes = person("adult_earnings_index", period)
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        emp_self_emp_ratio = person("emp_self_emp_ratio", period)

        for adult_index in range(1, 1 + adult_count):
            alt_sim = sim.get_branch(f"federal_mtr_for_adult_{adult_index}")
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
                employment_income + mask * delta * emp_self_emp_ratio,
            )
            alt_sim.set_input(
                "self_employment_income",
                period,
                self_employment_income + mask * delta * (1 - emp_self_emp_ratio),
            )
            alt_person = alt_sim.person
            alt_tax = alt_person.tax_unit("income_tax", period)
            increase = alt_tax - base_tax
            mtr_values += where(mask, increase / delta, 0)
            del sim.branches[f"federal_mtr_for_adult_{adult_index}"]
        return mtr_values


class state_marginal_tax_rate(Variable):
    label = "state marginal tax rate"
    documentation = (
        "Marginal change in state income tax per dollar of additional earnings."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        base_tax = person.tax_unit("state_income_tax", period)
        delta = parameters(period).simulation.marginal_tax_rate_delta
        adult_count = parameters(period).simulation.marginal_tax_rate_adults
        sim = person.simulation
        mtr_values = np.zeros(person.count, dtype=np.float32)
        adult_indexes = person("adult_earnings_index", period)
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        emp_self_emp_ratio = person("emp_self_emp_ratio", period)

        for adult_index in range(1, 1 + adult_count):
            alt_sim = sim.get_branch(f"state_mtr_for_adult_{adult_index}")
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
                employment_income + mask * delta * emp_self_emp_ratio,
            )
            alt_sim.set_input(
                "self_employment_income",
                period,
                self_employment_income + mask * delta * (1 - emp_self_emp_ratio),
            )
            alt_person = alt_sim.person
            alt_tax = alt_person.tax_unit("state_income_tax", period)
            increase = alt_tax - base_tax
            mtr_values += where(mask, increase / delta, 0)
            del sim.branches[f"state_mtr_for_adult_{adult_index}"]
        return mtr_values


class fica_marginal_tax_rate(Variable):
    label = "FICA marginal tax rate"
    documentation = (
        "Marginal change in employee payroll tax per dollar of additional earnings."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        base_tax = person.tax_unit("employee_payroll_tax", period)
        delta = parameters(period).simulation.marginal_tax_rate_delta
        adult_count = parameters(period).simulation.marginal_tax_rate_adults
        sim = person.simulation
        mtr_values = np.zeros(person.count, dtype=np.float32)
        adult_indexes = person("adult_earnings_index", period)
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        emp_self_emp_ratio = person("emp_self_emp_ratio", period)

        for adult_index in range(1, 1 + adult_count):
            alt_sim = sim.get_branch(f"fica_mtr_for_adult_{adult_index}")
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
                employment_income + mask * delta * emp_self_emp_ratio,
            )
            alt_sim.set_input(
                "self_employment_income",
                period,
                self_employment_income + mask * delta * (1 - emp_self_emp_ratio),
            )
            alt_person = alt_sim.person
            alt_tax = alt_person.tax_unit("employee_payroll_tax", period)
            increase = alt_tax - base_tax
            mtr_values += where(mask, increase / delta, 0)
            del sim.branches[f"fica_mtr_for_adult_{adult_index}"]
        return mtr_values
