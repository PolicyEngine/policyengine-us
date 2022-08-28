from openfisca_us.model_api import *


class mo_property_tax_credit_demographic_tests(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit demographic eligiblity test"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        #currently not including railroad retirement or veterans benefits. 
        rent_or_own = tax_unit("mo_property_tax_credit_rent_or_own", period)

        #determine if the tax unit head and spouse co-habitate
        lives_separately = tax_unit("lives_separately", period)
        living_arrangement = "SINGLE" if lives_separately > 0 else "JOINT"

        income_threshold = parameters(period).gov.states.mo.tax.credits.mo_property_tax_credit[rent_or_own][living_arrangement]
        income_test = total_household_income <= income_threshold

        rent = add(tax_unit, period, ["rent"])
        property_tax = tax_unit.household("real_estate_taxes", period)
        agi = tax_unit("adjusted_gross_income")
        benefits = tax_unit.spm_unit("spm_unit_benefits", period)
        total_household_income = agi + benefits

        rent_total = where(rent >= 750, 750, rent)
        property_tax_total = where(rent >= 1100, 1100, property_tax)
        total_credit_basis = where((rent_total + property_tax_total >= 1100), 1100, (rent_total + property_tax_total))

        minimum_base = parameters(period).gov.states.mo.tax.credits.mo_property_tax_credit_minimum_base
        maximum_upper_limit = parameters(period).gov.states.mo.tax.credits.mo_property_tax_credit_income_limits
        #check if rent/property tax > 1100
