from policyengine_us.model_api import *


class assigned_nm_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned New Mexico Premium Assistance for tax unit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    # Mirrors assigned_aca_ptc: the modeled subsidy is only received when the
    # eligible tax unit takes it up. Take-up is assigned at microdata
    # construction, so at the default take-up flag this equals the raw amount.
    reference = (
        "https://www.hca.nm.gov/health-insurance-marketplace-affordability-program/"
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("nm_premium_assistance", period) * tax_unit(
            "takes_up_nm_premium_assistance_if_eligible", period
        )
