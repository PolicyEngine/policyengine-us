from policyengine_us.model_api import *


class vt_renter_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Vermont renter credit"
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06066",  # (b)(1), (c)(3)
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2024.pdf#page=1",  # line 4
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # 32 V.S.A. 6066(b)(1) gives the credit to a claimant "who rented the
        # homestead", and (c)(3) requires at least six calendar months of
        # renting. PE-US has no months-rented input, so rent paid stands in for
        # both. A tenant whose subsidy covers all the rent also gets nothing
        # under (b)(1)(D), which pays a share of the gross rent the tenant paid.
        return add(tax_unit, period, ["rent"]) > 0
