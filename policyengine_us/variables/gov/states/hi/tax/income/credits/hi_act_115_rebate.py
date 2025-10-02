from policyengine_us.model_api import *


class hi_act_115_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii ACT 115 rebate"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://tax.hawaii.gov/act-115-ref/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.act_115_rebate
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        federal_agi = tax_unit("adjusted_gross_income", period)
        return select(
            [
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.SURVIVING_SPOUSE,
            ],
            [
                p.joint.calc(federal_agi),
                p.single.calc(federal_agi),
                p.single.calc(federal_agi),
                p.joint.calc(federal_agi),
            ],
            default=p.single.calc(federal_agi),
        )
