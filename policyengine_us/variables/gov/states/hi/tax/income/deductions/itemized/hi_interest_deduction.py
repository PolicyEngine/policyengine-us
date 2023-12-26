from policyengine_us.model_api import *


class hi_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii interest deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=17"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.interest.mortgage

        # 3. interest_deduction: worksheet A-3
        # Hawaii did not
        #     (1) suspend the deduction for interest paid on home equity loans
        #     (2) lower the dollar limit on mortgages qualifying for the home mortgage interest deduction
        filing_status = tax_unit("filing_status", period)
        home_mortgage_interest = min_(
            add(tax_unit, period, ["mortgage_interest"]),
            p.cap[filing_status],
        )
        investment_interest = add(
            tax_unit, period, ["investment_interest_expense"]
        )

        return max_(0, home_mortgage_interest + investment_interest)
