from openfisca_us.model_api import *


class nonbusiness_energy_property_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Nonbusiness energy property credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.residential_energy.nonbusiness
        if not p.in_effect:
            return 0
        improvements = tax_unit(
            "qualified_energy_efficiency_improvements_expenditures", period
        )
        improvements_credit = improvements * p.improvements.rate
        # Full property expenditures count for the credit.
        property_credit = tax_unit(
            "capped_residential_energy_property_expenditures", period
        )
        uncapped_credit = improvements_credit + property_credit
        # Apply lifetime limitation.
        prior_credits = tax_unit(
            "prior_nonbusiness_energy_property_credits", period
        )
        remaining_credit = p.cap.lifetime.total - prior_credits
        return min_(remaining_credit, uncapped_credit)
