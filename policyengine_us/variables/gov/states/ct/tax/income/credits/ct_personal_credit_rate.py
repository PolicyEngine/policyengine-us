from policyengine_us.model_api import *


class ct_personal_credit_rate(Variable):
    value_type = float
    entity = TaxUnit
    unit = "\1"
    label = "Connecticut personal credit rate"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ct_agi", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.credits.agi

        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.widow.calc(agi, right=True),
                p.head_of_household.calc(agi, right=True),
            ],
        )
