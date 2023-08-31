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
        ).gov.states.wv.tax.income.credits.low_income_family_tax_credit

        wv_agi = tax_unit("wv_agi", period)
        # max family size limit
        n = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        family_size = min_(n, p.max_family_size)
        fpg = p1 + pn * (family_size - 1)

        # modified agi limit
        fpg_amount = p.fpg_percent * fpg
        reduced_agi = wv_agi - fpg_amount

        return select(
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
                p.amount.head.calc(reduced_agi),
                p.amount.widow.calc(reduced_agi),
            ],
        )
