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
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mt.tax.income.subtractions
        total_benefit_fraction = p.social_security.total_benefit_fraction1
        
        # calculate subtraction amount
        # ... US-taxable social security benefits
        us_taxable_oasdi = add(tax_unit, period, ["taxable_social_security"])
        net_benefits = add(tax_unit, period, ["household_benefits"]) #need adjustment

        us_gross_income = add(tax_unit, period, ["irs_gross_income"])#total income (may need adjustment)
        adj_income = us_gross_income - us_taxable_oasdi

        total_oasdi = add(tax_unit, period, ["social_security"])
        oasdi_amount = total_oasdi * total_benefit_fraction
        tax_exempt_int = add(tax_unit, period, ["tax_exempt_interest_income"])
        sum_income = adj_income + oasdi_amount + tax_exempt_int

        us_ald = tax_unit("above_the_line_deductions", period)
        student_loan_int = add(tax_unit, period, ["student_loan_interest"])
        mn_ald = max_(0, us_ald - student_loan_int)
        income = max_(0, sum_income - mn_ald)
        
        net_income = max_(0, income - income_amount)
        alt_sub_amt = max_(0, alt_amount - (net_income * net_income_fraction))
        return min_(us_taxable_oasdi, alt_sub_amt)