from policyengine_us.model_api import *


class ct_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut property tax credit"
    unit = USD
    definition_period = YEAR
    reference = ()
    defined_for = "ct_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ct_agi", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        # line 63(total property tax)
        property_tax = tax_unit("ct_property_tax", period)
        # line 64 (maximum property tax)
        max_amount = p.max_amount
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
        earned_credit = where(
            agi < min_agi, max_credit, max_credit - (max_credit * percent)
        )
        return earned_credit
