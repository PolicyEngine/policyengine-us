from openfisca_us.model_api import *


class energy_efficient_home_improvement_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Nonbusiness energy property credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        if not p.in_effect:
            return 0
        improvements = tax_unit(
            "qualified_energy_efficiency_improvements_expenditures", period
        )
        improvements_credit = improvements * p.rates.improvements
        property_expenditures = tax_unit(
            "capped_residential_energy_property_expenditures", period
        )
        property_credit = property_expenditures * p.rates.property
        uncapped_credit = improvements_credit + property_credit
        # Apply lifetime limitation.
        prior_credits = tax_unit(
            "prior_energy_efficient_home_improvement_credits", period
        )
        remaining_credit = p.cap.lifetime.total - prior_credits
        return min_(remaining_credit, uncapped_credit)
