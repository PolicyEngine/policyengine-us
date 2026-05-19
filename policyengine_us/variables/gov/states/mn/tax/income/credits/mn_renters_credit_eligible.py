from policyengine_us.model_api import *


class mn_renters_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Minnesota renter's credit"
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ref-25.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        household_income = tax_unit("mn_renters_credit_household_income", period)
        rent_constituting_property_taxes = tax_unit(
            "mn_rent_constituting_property_taxes", period
        )
        qualifying_crp = tax_unit("mn_renters_credit_qualifying_crp", period)
        property_tax_exempt = tax_unit("mn_renters_credit_property_tax_exempt", period)
        p = parameters(period).gov.states.mn.tax.income.credits.renters

        claimants = tax_unit.members("is_tax_unit_head_or_spouse", period)
        claimant_is_tax_unit_dependent = tax_unit.any(
            claimants & tax_unit.members("is_tax_unit_dependent", period)
        )
        claimant_is_dependent_elsewhere = tax_unit(
            "head_is_dependent_elsewhere", period
        ) | tax_unit("spouse_is_dependent_elsewhere", period)
        claimant_is_dependent = (
            claimant_is_tax_unit_dependent | claimant_is_dependent_elsewhere
        )

        return (
            qualifying_crp
            & (rent_constituting_property_taxes > 0)
            & ~claimant_is_dependent
            & ~property_tax_exempt
            & (p.max_credit.calc(household_income) > 0)
        )
