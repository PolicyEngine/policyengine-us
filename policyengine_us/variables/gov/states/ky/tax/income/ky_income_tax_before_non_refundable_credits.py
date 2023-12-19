from policyengine_us.model_api import *


class ky_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, paramters):
        joint_filing = (
            tax_unit("filing_status", period)
            == tax_unit("filing_status", period).possible_values.JOINT
        )
        person = tax_unit.members
        person_income = where(
            joint_filing,
            person("ky_taxable_income_joint", period),
            person("ky_taxable_income_indiv", period),
        )
        income = tax_unit.sum(person_income)
        rate = paramters(period).gov.states.ky.tax.income.rate
        return income * rate
