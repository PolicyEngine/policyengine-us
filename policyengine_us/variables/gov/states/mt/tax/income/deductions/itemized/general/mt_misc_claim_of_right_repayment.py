from policyengine_us.model_api import *


class mt_misc_claim_of_right_repayment(Variable):
    value_type = float
    entity = Person
    label = "Montana claim of right repayment subject to the miscellaneous floor"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-26/section-1.1341-1#p-1.1341-1(a)(3)",
        "https://mtrevenue.gov/wp-content/uploads/2018/02/2017-Form2-with-Legal-References.pdf#page=6",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.misc_floor_applies:
            return 0
        on_return = person("is_tax_unit_head_or_spouse", period)
        repayment = max_(0, person("claim_of_right_repayment", period)) * on_return
        income_class = person("mt_claim_of_right_repayment_income_class", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_class = person.tax_unit.sum(income_class * head)
        spouse_class = person.tax_unit.sum(income_class * spouse)
        same_class = head_class == spouse_class
        # The $3,000 test applies to each income class on the federal return,
        # including both spouses, rather than to individual repayments.
        class_total = where(same_class, person.tax_unit.sum(repayment), repayment)
        threshold = parameters(
            period
        ).gov.irs.deductions.itemized.claim_of_right.threshold
        return repayment * (class_total <= threshold)
