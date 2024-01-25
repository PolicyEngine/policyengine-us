from policyengine_us.model_api import *


class wv_low_income_family_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia low-income family tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "wv_low_income_family_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        p = parameters(
            period
        ).gov.states.wv.tax.income.credits.liftc  # low_income_family_tax_credit

        wv_agi = tax_unit("wv_low_income_family_tax_credit_agi", period)
        fpg = tax_unit("wv_low_income_family_tax_credit_fpg", period)
        # modified agi limit
        fpg_amount = p.fpg_percent[filing_status] * fpg
        # condition: wv_agi < = fpg_amount
        reduced_agi = wv_agi - fpg_amount

        credit_percentage = select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.WIDOW,
            ],
            [
                p.amount.single.calc(reduced_agi),
                p.amount.separate.calc(reduced_agi),
                p.amount.joint.calc(reduced_agi),
                p.amount.head_of_household.calc(reduced_agi),
                p.amount.widow.calc(reduced_agi),
            ],
        )

        tax_before_credits = tax_unit(
            "wv_income_tax_before_non_refundable_credits", period
        )
        return tax_before_credits * credit_percentage
