from openfisca_us.model_api import *

class mo_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        ##Eligibility
        #vars for age test
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_age_test = age_head >= 65
        spouse_age_test = age_spouse >= 65
        age_test = (head_age_test + spouse_age_test) >= 1

        #vars for disabled test
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        disabled_test = (disabled_head + disabled_spouse) >= 1

        #vars for military disabled test
        military_disabled_head = tax_unit("military_disabled_head", period)
        military_disabled_spouse = tax_unit("military_disabled_spouse", period)
        military_disabled_test = (military_disabled_head + military_disabled_spouse) >= 1

        #vars for surviving spouse benefits test
        #might need to check for only head? not sure how this would work in practice, could more than the head have suvivor benefits in a tax_unit?
        surivor_benefits = tax_unit.members("social_security_survivors", period)
        survivor_benefit_test = surivor_benefits > 0

        #rent or property_tax test
        rent = add(tax_unit, period, ["rent"])
        property_tax = tax_unit.household("real_estate_taxes", period)
        any_housing_cost = rent + property_tax > 0
        demographic_qualification = (age_test + disabled_test + military_disabled_test + survivor_benefit_test) >= 1
        housing_and_demographic_test = (any_housing_cost + demographic_qualification) == 2

        #determine which income test to use. 1 is "OWNER", 0 is "RENTER"
        housing_status = where(property_tax > rent, 'OWNER', 'RENTER')
        lives_separately = tax_unit("lives_separately", period)
        living_arrangement = "SINGLE" if lives_separately > 0 else "JOINT"

        #MO agi has the same definition as Federal AGI, as we are not modeling 
        #additions and subtractions (none of interest)
        agi = tax_unit("adjusted_gross_income")
        benefits = tax_unit.spm_unit("spm_unit_benefits", period)
        total_household_income = agi + benefits
 
        #currently not including railroad retirement or veterans benefits. 
        income_threshold = parameters(period).gov.states.mo.tax.credits.mo_property_tax_credit[housing_status][living_arrangement]
        income_test = total_household_income <= income_threshold
        
        rent_total = where(rent >= 750, 750, rent)
        property_tax_total = where(rent >= 1100, 1100, property_tax)
        total_credit_basis = where((rent_total + property_tax_total >= 1100), 1100, (rent_total+property_tax_total))


        minimum_base = parameters(period).gov.states.mo.tax.credits.mo_property_tax_credit_minimum_base
        maximum_upper_limit = parameters(period).gov.states.mo.tax.credits.mo_property_tax_credit_income_limits
        #check if rent/property tax > 1100
        where(housing_and_demographic_test == 1, where(income_test == 1, ))

        

        