from policyengine_us.model_api import *


class mt_misc_deductions_subject_to_floor_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana miscellaneous deductions after the joint return AGI floor"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/2018/02/2017-Form2-with-Legal-References.pdf#page=6"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.misc_floor_applies:
            return 0
        person = tax_unit.members
        on_return = person("is_tax_unit_head_or_spouse", period)
        # Use raw expenses: the federal misc_deduction already subtracts a
        # floor based on federal AGI, which can differ from Montana AGI.
        pool = add(
            person,
            period,
            [
                "mt_misc_claim_of_right_repayment",
                "unreimbursed_business_employee_expenses",
                "tax_preparation_fees",
            ],
        )
        expenses = tax_unit.sum(pool * on_return)
        agi = tax_unit("mt_agi_joint", period)
        return max_(0, expenses - p.misc_floor * agi)
