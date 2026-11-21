from policyengine_us.model_api import *


class vt_renter_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Vermont renter credit"
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06066",  # (b)(1), (c)(3)
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2025.pdf#page=1",  # lines 2, 4, 7
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        pays_rent = add(tax_unit, period, ["rent"]) > 0
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        reported_period = p.reported_rental_period
        if reported_period.in_effect:
            months_rented = tax_unit("vt_renter_credit_months_rented", period)
            meets_duration = (months_rented == -1) | (
                (months_rented >= reported_period.minimum_months_rented)
                & (months_rented <= MONTHS_IN_YEAR)
            )
            domicile = tax_unit("vt_renter_credit_domicile_status", period)
            meets_domicile = domicile != domicile.possible_values.NOT_FULL_YEAR
            return pays_rent & meets_duration & meets_domicile
        return pays_rent
