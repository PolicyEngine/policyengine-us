from policyengine_us.model_api import *


class ar_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas standard deduction when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
    defined_for = StateCode.AR

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
                fsvals.SEPARATE,  # couples are filing separately on Arkansas form
                fsvals.SINGLE,
                fsvals.SEPARATE,
                fsvals.HEAD_OF_HOUSEHOLD,
                fsvals.WIDOW,
            ],
        )
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        p = parameters(period).gov.states.ar.tax.income.deductions
        return (is_head | is_spouse) * p.standard[filing_status]
