from policyengine_us.model_api import *


class mt_misc_deductions_subject_to_floor_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana miscellaneous deductions after the separate return AGI floor"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/2018/02/2017-Form2-with-Legal-References.pdf#page=6"
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.misc_floor_applies:
            return 0
        pool = add(
            person,
            period,
            [
                "mt_misc_claim_of_right_repayment",
                "unreimbursed_business_employee_expenses",
                "tax_preparation_fees",
            ],
        )
        agi = person("mt_agi_indiv", period)
        on_return = person("is_tax_unit_head_or_spouse", period)
        return on_return * max_(0, pool - p.misc_floor * agi)
