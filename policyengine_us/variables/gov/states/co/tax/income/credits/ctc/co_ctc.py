from policyengine_us.model_api import *


class co_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = ""
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        person = tax_unit.members
        # The co ctc amount is based on agi, federal ctc amount and number of eligible children.
        agi = tax_unit("adjusted_gross_income", period)
        federal_ctc = tax_unit("ctc", period)

        eligible_child = person("age", period) < p.age_threshold
        eligible_children = tax_unit.sum(eligible_child)

        rate = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
            ],
        )
        return rate * federal_ctc * eligible_children
