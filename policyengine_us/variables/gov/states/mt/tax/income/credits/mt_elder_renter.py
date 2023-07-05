from policyengine_us.model_api import *


class mt_elder_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Elderly Homeowner/Renter Credit"
    unit = USD
    documentation = ""
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # Check eligibility based on state, rent, filing status, and income.
        p = parameters(period).gov.states.mt.tax.income.credits.elder_renter_credit
        #agi = tax_unit("mt_agi", period)

        #Check the eligibility
        age=
        gross_household_income=
        
        
        #Calculate net_household_income
        standard_exclusion=p.standard_exlusion
        temp1 = max_(gross_household_income-standard_exclusion, 0)
        net_household_income=p.household_income_reduction[temp1]*temp1

        #Credit Computation
        property_tax=
        rent=add(tax_unit, period, ["rent"])
        temp2=min_(rent*0.15+property_tax, 1150)
        total=p.credit_multiplier[temp2]*temp2

        return eligible * total