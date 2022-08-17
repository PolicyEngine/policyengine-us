from openfisca_us.model_api import *


class nonbusiness_energy_property_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Nonbusiness energy property credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"

    def formula(tax_unit, period, parameters):
        
        uncapped_credit = 
        # Apply lifetime limitation.
        prior_credits = tax_unit("prior_nonbusiness_energy_property_credits", period)
        lifetime_limit = parameters(
            period
        ).gov.irs.credits.residential_energy.nonbusiness.limit.lifetime
        remaining_credit = lifetime_limit - prior_credits
        return min_(remaining_credit, uncapped_credit)