from policyengine_us.model_api import *


class md_senior_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Senior Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=15"
    defined_for = "md_senior_tax_credit_eligible"

    def formula_2022(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.senior_tax

        age_head = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        head_eligible = (age_head >= p.age_eligibility).astype(int)
        spouse_eligible = (spouse_age >= p.age_eligibility).astype(int)
        eligible_count = head_eligible + spouse_eligible

        credit_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.amount.single,
                p.amount.joint[eligible_count],
                p.amount.head_of_household,
                p.amount.widow,
                p.amount.separate,
            ],
        )
        return where(eligible_count > 0, credit_amount, 0)
