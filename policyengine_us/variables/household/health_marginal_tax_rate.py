from policyengine_us.model_api import *

class health_marginal_tax_rate(Variable):
    """
    Fraction of marginal earnings that do **not** raise net household
    resources once cash + health benefits are taken into account.
    """
    label = "Marginal tax rate including health benefits"
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        # --- Baseline household resources ------------------------------------
        hh = person.household
        netinc_base = (
            hh("household_net_income", period)
            + hh("healthcare_benefit_value", period)
        )

        # --- Simulation parameters ------------------------------------------
        delta       = parameters(period).simulation.marginal_tax_rate_delta
        adult_count = parameters(period).simulation.marginal_tax_rate_adults
        sim         = person.simulation

        # --- Pre-compute earnings split --------------------------------------
        employment_income     = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        total_earnings        = employment_income + self_employment_income
        emp_self_emp_ratio = np.divide(
            employment_income,
            total_earnings,
            out=np.ones_like(total_earnings, dtype=np.float32),
            where=total_earnings > 0,
        )

        mtr_values   = np.zeros(person.count, dtype=np.float32)
        adult_idx_by_earnings = person("adult_earnings_index", period)

        # --- Loop over up to `adult_count` adults ----------------------------
        for idx in range(1, 1 + adult_count):
            branch = sim.get_branch(f"mtr_health_for_adult_{idx}")

            # Force re-computation of everything except explicit inputs
            for var in sim.tax_benefit_system.variables:
                if var not in sim.input_variables or var == "employment_income":
                    branch.delete_arrays(var)

            mask = adult_idx_by_earnings == idx

            # Small bump to earnings for this adult
            branch.set_input(
                "employment_income",
                period,
                employment_income + mask * delta * emp_self_emp_ratio,
            )
            branch.set_input(
                "self_employment_income",
                period,
                self_employment_income + mask * delta * (1 - emp_self_emp_ratio),
            )

            alt_person = branch.person
            hh_alt = alt_person.household

            # --- Household resources in the alternative scenario -------------
            netinc_alt = (
                hh_alt("household_net_income", period)
                + hh_alt("healthcare_benefit_value", period)
            )

            increase = netinc_alt - netinc_base
            mtr_values += np.where(mask, 1 - increase / delta, 0.0)

            # Clean up the branch so memory use doesn’t explode
            del sim.branches[f"mtr_health_for_adult_{idx}"]

        return mtr_values
