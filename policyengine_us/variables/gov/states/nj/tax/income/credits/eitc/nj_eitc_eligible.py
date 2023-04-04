from policyengine_us.model_api import *


class nj_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Eligible for EITC"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Return eitc_eligible with modified age conditions based on NJ parameters.

        # Set up simulation clone
        simulation = tax_unit.simulation
        simulation.max_spiral_loops = 10
        simulation._check_for_cycle = lambda *args: None

        simulation.get_holder("eitc_eligible").delete_arrays()

        # Modify EITC min age condition.
        original_min_age = simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.min(
            period
        )
        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.min.update(
            value=parameters(
                period
            ).gov.states.nj.tax.income.credits.eitc.eligibility.age.min,
            period=period,
        )

        # Modify EITC max age condition.
        original_max_age = simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.max(
            period
        )
        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.max.update(
            value=parameters(
                period
            ).gov.states.nj.tax.income.credits.eitc.eligibility.age.max,
            period=period,
        )

        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc._at_instant_cache = (
            {}
        )

        eitc_eligible = simulation.calculate("eitc_eligible", period)
        simulation.get_holder("eitc_eligible").delete_arrays()

        # Reset EITC min age condition.
        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.min.update(
            value=original_min_age,
            period=period,
        )

        # Reset EITC max age condition.
        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.max.update(
            value=original_max_age,
            period=period,
        )

        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc._at_instant_cache = (
            {}
        )
        return eitc_eligible
