from policyengine_us.model_api import *


class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = "The tax liability used to determine the maximum amount of the non-refundable CTC. Excludes SALT from all calculations (this is an inaccuracy required to avoid circular dependencies)."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        no_salt_branch = simulation.get_branch("no_salt")
        no_salt_branch.tax_benefit_system.variables[
            "salt_deduction"
        ].is_neutralized = True
        tax_liability_before_credits = no_salt_branch.calculate(
            "income_tax_before_credits", period
        )
        non_refundable_credits = parameters(
            period
        ).gov.irs.credits.non_refundable
        total_credits = sum(
            [
                tax_unit(credit, period)
                for credit in non_refundable_credits
                if credit not in ("non_refundable_ctc",)
            ]
        )
        simulation.tax_benefit_system.variables[
            "salt_deduction"
        ].is_neutralized = False

        return max_(0, tax_liability_before_credits - total_credits)
