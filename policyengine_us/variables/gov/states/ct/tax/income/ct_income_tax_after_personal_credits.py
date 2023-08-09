from policyengine_us.model_api import *


class ct_income_tax_after_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax after personal tax credits and exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ct_agi", period)
        personal_exemptions = tax_unit("ct_personal_exemptions", period)
        income_after_personal_exemptions = max_(
            income - personal_exemptions, 0
        )
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.main
        income_after_tax_rate = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(income_after_personal_exemptions),
                p.joint.calc(income_after_personal_exemptions),
                p.separate.calc(income_after_personal_exemptions),
                p.widow.calc(income_after_personal_exemptions),
                p.head_of_household.calc(income_after_personal_exemptions),
            ],
        )
        add_back = tax_unit("ct_income_tax_phase_out_add_back", period)
        tax_recapture = tax_unit("ct_income_tax_recapture", period)
        total_add_back = income_after_tax_rate + add_back + tax_recapture
        personal_credits = tax_unit("ct_personal_credits", period)
        presonal_credit_amount = personal_credits * total_add_back
        return max_(total_add_back - presonal_credit_amount, 0)
