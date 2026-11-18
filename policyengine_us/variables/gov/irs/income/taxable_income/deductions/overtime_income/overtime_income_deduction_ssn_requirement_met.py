from policyengine_us.model_api import *


class overtime_income_deduction_ssn_requirement_met(Variable):
    value_type = bool
    entity = TaxUnit
    label = "SSN requirement met for the overtime income deduction"
    documentation = "Whether a filer (a tax unit member who is not a dependent) has a Social Security number valid for the overtime income deduction. Only overtime received by such a filer counts; see overtime_income_deduction_eligible_person."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/225#d_1"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible = person("overtime_income_deduction_eligible_person", period)
        return tax_unit.any(eligible)
