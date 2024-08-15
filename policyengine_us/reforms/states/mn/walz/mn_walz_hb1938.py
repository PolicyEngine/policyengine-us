from policyengine_us.model_api import *


def create_mn_walz_hb1938() -> Reform:

    class mn_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota refundable income tax credits"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_21.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_22.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            if period.start >= 2032:
                instant_str = f"2032-01-01"
            else:
                instant_str = period
            p = parameters(instant_str).gov.states.mn.tax.income.credits
            return add(tax_unit, period, p.refundable)

    class mn_social_security_subtraction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota social security subtraction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            # specify parameters
            filing_status = tax_unit("filing_status", period)
            p = parameters(period).gov.states.mn.tax.income.subtractions
            total_benefit_fraction = p.social_security.total_benefit_fraction
            income_amount = p.social_security.income_amount[filing_status]
            net_income_fraction = p.social_security.net_income_fraction
            alt_amount = p.social_security.alternative_amount[filing_status]
            # calculate subtraction amount (following "Worksheet for line 12")
            # ... US-taxable social security benefits
            us_taxable_oasdi = add(
                tax_unit, period, ["taxable_social_security"]
            )
            # ... alternative benefit subtraction amount
            us_gross_income = add(tax_unit, period, ["irs_gross_income"])
            adj_income = us_gross_income - us_taxable_oasdi
            total_oasdi = add(tax_unit, period, ["social_security"])
            oasdi_amount = total_oasdi * total_benefit_fraction
            tax_exempt_int = add(
                tax_unit, period, ["tax_exempt_interest_income"]
            )
            sum_income = adj_income + oasdi_amount + tax_exempt_int
            us_ald = tax_unit("above_the_line_deductions", period)
            student_loan_int = add(tax_unit, period, ["student_loan_interest"])
            mn_ald = max_(0, us_ald - student_loan_int)
            income = max_(0, sum_income - mn_ald)
            net_income = max_(0, income - income_amount)
            alt_sub_amt = max_(
                0, alt_amount - (net_income * net_income_fraction)
            )
            return min_(us_taxable_oasdi, alt_sub_amt)

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("mn_public_pension_subtraction")
            self.update_variable(mn_social_security_subtraction)
            self.update_variable(mn_refundable_credits)

    return reform


def create_mn_walz_hb1938_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mn_walz_hb1938()

    p = parameters(period).gov.contrib.states.ny.wftc

    if p.in_effect:
        return create_mn_walz_hb1938()
    else:
        return None


mn_walz_hb1938 = create_mn_walz_hb1938_reform(None, None, bypass=True)
