from policyengine_us.model_api import *


class nj_staynj_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Stay NJ Property Tax Credit program eligibility"
    definition_period = YEAR
    reference = (
        "https://pub.njleg.state.nj.us/Bills/2022/PL23/75_.HTM",
        "https://www.nj.gov/treasury/taxation/staynj/index.shtml",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.staynj

        # Age 65+ for head or spouse
        greater_age = tax_unit("greater_age_head_spouse", period)
        age_eligible = greater_age >= p.age_threshold

        # Gross income below limit (strict less than per statute)
        gross_income = add(tax_unit, period, ["nj_gross_income"])
        income_eligible = gross_income < p.income_limit

        # Must be homeowner (pays property taxes, not renter)
        pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
        pays_rent = tax_unit("rents", period)
        is_homeowner = pays_property_taxes & ~pays_rent

        return age_eligible & income_eligible & is_homeowner
