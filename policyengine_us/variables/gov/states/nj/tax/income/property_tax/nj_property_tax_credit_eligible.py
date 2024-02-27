from policyengine_us.model_api import *


class nj_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey property tax credit eligibility"
    definition_period = YEAR
    reference = "https://www.state.nj.us/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=25"

    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.property_tax

        # determine if pays property taxes via home ownership or renting
        owner_pays_ptax = add(tax_unit, period, ["real_estate_taxes"]) > 0
        renter_pays_ptax = tax_unit("rents", period)
        pays_ptax = owner_pays_ptax | renter_pays_ptax

        # if filing jointly, only one spouse needs to be 65+ or blind/disabled
        blind_head = tax_unit("blind_head", period)
        disabled_head = tax_unit("disabled_head", period)
        blind_spouse = tax_unit("blind_spouse", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        senior_head = tax_unit("age_head", period) >= p.senior_qualifying_age
        senior_spouse = (
            tax_unit("age_spouse", period) >= p.senior_qualifying_age
        )
        senior_blind_disabled = (
            blind_head
            | disabled_head
            | blind_spouse
            | disabled_spouse
            | senior_head
            | senior_spouse
        )

        # return eligiblity for property tax credit
        deduction_eligibility = tax_unit(
            "nj_property_tax_deduction_eligible", period
        )
        return deduction_eligibility | (pays_ptax & senior_blind_disabled)
