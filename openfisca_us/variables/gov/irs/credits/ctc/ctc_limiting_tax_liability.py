from openfisca_us.model_api import *
from openfisca_core.taxbenefitsystems import TaxBenefitSystem

class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = "The tax liability used to determine the maximum amount of the non-refundable CTC. Excludes SALT from all calculations (this is an inaccuracy required to avoid circular dependencies)."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        non_refundable_credits = parameters(
            period
        ).gov.irs.credits.non_refundable
        total_credits = sum(
            [
                tax_unit(credit, period)
                for credit in non_refundable_credits
                if credit != "non_refundable_ctc"
            ]
        )
        simulation = tax_unit.simulation.clone()
        simulation.tax_benefit_system.neutralize_variable("salt_deduction")
        tax_liability = simulation.calculate("income_tax_before_credits", period)
        return max_(0, tax_liability - total_credits)
