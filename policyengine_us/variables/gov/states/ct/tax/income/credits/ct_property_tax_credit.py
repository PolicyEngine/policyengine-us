from policyengine_us.model_api import *


class ct_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "CT property tax credit"
    unit = USD
    definition_period = YEAR
    reference = ()
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ct_agi", period)
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        age = person("age", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        # line 63(total property tax)
        property_tax = tax_unit("ct_property_tax", period)
        # line 64 (maximum property tax)
        max_amount = p.max_amount
        age_threshold = p.threshold.age_minimum
        min_agi = p.threshold.agi[filing_status]
        # line 65 (lesser of max_amount and property tax)
        max_credit = min_(property_tax, max_amount)
        # line 66
        percent = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.amount.single.calc(agi),
                p.amount.joint.calc(agi),
                p.amount.separate.calc(agi),
                p.amount.widow.calc(agi),
                p.amount.head_of_household.calc(agi),
            ],
        )

        if age < age_threshold:
            return 0
        else:
            if agi < min_agi:
                return max_credit
            # line 67 (multiply 65 and 66)
            non_refudable_portion = max_credit * percent
            # line 68
            return max_credit - non_refudable_portion
