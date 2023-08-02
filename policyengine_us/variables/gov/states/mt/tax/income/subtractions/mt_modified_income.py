from policyengine_us.model_api import *


class mt_modified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana modified income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf"
        ""
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # specify parameters
        p = parameters(period).gov.states.mt.tax.income.subtractions
        total_benefit_fraction = p.social_security.total_benefit_fraction1
        
        #Line1
        net_benefits = add(tax_unit, period, ["spm_unit_benefits"])
        
        #Line3
        us_taxable_oasdi = tax_unit(period, ["taxable_social_security"])
        total_income = tax_unit(period, ["mt_total_income"])
        adj_income = total_income - us_taxable_oasdi

        mt_agi_additions=tax_unit(period, ["mt_agi_additions"])
        interest_income=tax_unit(period, ["interest_income"])
        adj_additions=mt_agi_additions-interest_income

        tax_exempt_int = add(tax_unit, period, ["tax_exempt_interest_income"])
        
        #Line6
        sum_income = net_benefits*total_benefit_fraction +adj_income + adj_additions + tax_exempt_int
        
        #Line7
        mt_adjustments=tax_unit(period, ["mt_adjustments"])
        student_loan_int = add(tax_unit, period, ["student_loan_interest"])
        
        #Line8
        mt_agi_subtractions=tax_unit(period, ["mt_agi_subtractions"])
        
        return mt_agi_subtractions+mt_adjustments-student_loan_int-sum_income