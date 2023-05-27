from policyengine_us.model_api import *


class nj_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey property tax credit eligibility"
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Same as deduction eligibility, but also eligible if 65+ or
        # blind/disabled and paid property taxes.
        deduction_eligibility = tax_unit(
            "nj_property_tax_deduction_eligible", period
        )

        # Get the NJ property tax credit portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.credits.property_tax

        # If filing jointly, only one spouse needs to be 65+ or blind/disabled.
        blind_head = tax_unit("blind_head", period)
        disabled_head = tax_unit("disabled_head", period)
        blind_spouse = tax_unit("blind_spouse", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        senior_head = tax_unit("age_head", period) > p.senior_qualifying_age
        senior_spouse = (
            tax_unit("age_spouse", period) > p.senior_qualifying_age
        )
        senior_blind_disabled = (
            blind_head
            | disabled_head
            | blind_spouse
            | disabled_spouse
            | senior_head
            | senior_spouse
        )

        # Next check if they paid property taxes (either directly or through
        # rent).
        direct_property_taxes = tax_unit("nj_homeowners_property_tax", period)
        rent = tax_unit("rents", period)
        paid_property_taxes = (direct_property_taxes + rent) > 0

        return deduction_eligibility | (
            senior_blind_disabled & paid_property_taxes
        )
