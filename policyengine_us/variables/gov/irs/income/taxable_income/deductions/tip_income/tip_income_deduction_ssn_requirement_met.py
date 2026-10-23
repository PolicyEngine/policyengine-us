from policyengine_us.model_api import *


class tip_income_deduction_ssn_requirement_met(Variable):
    value_type = bool
    entity = TaxUnit
    label = "SSN requirement met for the tip income deduction"
    documentation = "Whether the head or spouse has a Social Security number valid for the tip income deduction. Only tips received by such a head or spouse count; see tip_income_deduction_eligible_person."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/224#e_1"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible = person("tip_income_deduction_eligible_person", period)
        return tax_unit.any(eligible)
