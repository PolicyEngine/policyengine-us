from policyengine_us.model_api import *


class mn_renters_credit_total_rent_from_crps(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit total rent from CRPs"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf"
    )

    def formula(tax_unit, period, parameters):
        gross_rent = max_(
            add(tax_unit, period, ["pre_subsidy_rent"]),
            add(tax_unit, period, ["rent"]),
        )
        shared_rent_fraction = tax_unit(
            "mn_renters_credit_shared_rent_fraction", period
        )
        return gross_rent * shared_rent_fraction
