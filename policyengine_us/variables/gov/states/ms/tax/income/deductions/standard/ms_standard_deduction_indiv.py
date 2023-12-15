from policyengine_us.model_api import *


class ms_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Mississippi standard deduction when married couples file separately"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        us_filing_status = person.tax_unit("filing_status", period)
        fsvals = us_filing_status.possible_values
        filing_status = select(
            [
                us_filing_status == fsvals.JOINT,
                us_filing_status == fsvals.SINGLE,
                us_filing_status == fsvals.SEPARATE,
                us_filing_status == fsvals.HEAD_OF_HOUSEHOLD,
                us_filing_status == fsvals.WIDOW,
            ],
            [
                fsvals.SEPARATE,  # couples are filing separately on Missippi form
                fsvals.SINGLE,
                fsvals.SEPARATE,
                fsvals.HEAD_OF_HOUSEHOLD,
                fsvals.WIDOW,
            ],
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.ms.tax.income.deductions.standard
        return head_or_spouse * p.amount[filing_status]
