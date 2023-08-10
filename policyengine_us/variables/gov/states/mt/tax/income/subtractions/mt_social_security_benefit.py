from policyengine_us.model_api import *


class mt_social_security_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf"
        ""
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # specify parameters
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mt.tax.income.subtractions
        total_benefit_fraction1 = p.social_security.total_benefit_fraction1
        total_benefit_fraction2 = p.social_security.total_benefit_fraction2
        modified_income_cap = p.social_security.modified_income_cap[filing_status]
        exceeding_income_cap = p.social_security.exceeding_income_cap[filing_status]
        exceeding_income_fraction = p.social_security.exceeding_income_fraction
        extra_income_fraction = p.social_security.extra_income_fraction

        net_benefits = tax_unit.spm_unit("spm_unit_benefits", period)
        modified_income = tax_unit("mt_modified_income", period)

        #if modified_income is less than cap, return 0
        exceeding_income = modified_income - modified_income_cap
        eligibility = (exceeding_income >= 0)

        #Calculate the Montana Taxable Social Security Benefits
        extra_income = max_(exceeding_income - exceeding_income_cap, 0) #Line 13
        temp1 = min_(exceeding_income, exceeding_income_cap) #Line 14
        temp2 = min_(temp1 * exceeding_income_fraction, net_benefits * total_benefit_fraction1) #Line 16
        temp3 = extra_income * extra_income_fraction + temp2 #Line 18

        return eligibility * min_(temp3, net_benefits * total_benefit_fraction2)
        