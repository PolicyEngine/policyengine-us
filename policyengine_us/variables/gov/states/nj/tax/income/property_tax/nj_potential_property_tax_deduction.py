from policyengine_us.model_api import *


class nj_potential_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey potential property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/"
    defined_for = "nj_property_tax_deduction_or_credit_eligible"

    def formula(tax_unit, period, parameters):
        # Don't forget to divide the threshold if filing separately? They have to also live together.

        # Get the NJ property tax deduction portion of the parameter tree.
        p = parameters(
            period
        ).gov.states.nj.tax.income.property_tax_deduction_credit

        # Determine whether the tax unit is renting or owns a home.
        rents = tax_unit("rents", period)

        # Get the amount of property tax paid by the tax unit.
        # If renting, this will be a fraction of the total rent.
        property_tax = np.where(
            rents,
            tax_unit("rent", period) * p.rent_fraction,
            tax_unit("nj_homeowners_property_tax", period),
        )

        # Get the amount of paid property taxes under the threshold.
        threshold = p.deductible_property_taxes_threshold

        return min_(property_tax, threshold)
