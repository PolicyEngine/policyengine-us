from policyengine_us.model_api import *


class nj_potential_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey potential property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/"
    defined_for = "nj_property_tax_deduction_eligible"

    def formula(tax_unit, period, parameters):
        # Get the NJ property tax deduction portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.deductions.property_tax

        # Determine whether the tax unit is renting or owns a home.
        rents = tax_unit("rents", period)

        # Get the amount of property tax paid by the tax unit.
        # If renting, this will be a fraction of the total rent.
        person = tax_unit.members
        rent_amounts = person("rent", period)
        property_tax = where(
            rents,
            tax_unit.sum(rent_amounts) * p.qualifying_rent_fraction,
            tax_unit("nj_homeowners_property_tax", period),
        )

        # If filing separate but maintain same home, halve property tax.
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        property_tax = property_tax / (1 + separate * cohabitating)

        # Get the amount of paid property taxes under the threshold.
        # Threshold is also halved if filing separate but maintain same home.
        threshold = p.threshold / (1 + separate * cohabitating)

        return min_(property_tax, threshold)
