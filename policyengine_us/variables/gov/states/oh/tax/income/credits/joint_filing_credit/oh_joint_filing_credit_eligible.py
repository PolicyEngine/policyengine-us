from policyengine_us.model_api import *


class oh_joint_filing_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Ohio Joint Filing Credit"
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.05"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.joint_filing_credit
        income = person("employment_income", period)

        head_income = tax_unit.sum(is_head * income)

        spouse_income = tax_unit.sum(is_spouse * income)

        income_eligible = (head_income >= p.income_threshold) & (
            spouse_income >= p.income_threshold
        )
        status_eligible = filing_status == filing_status.possible_values.JOINT

        return income_eligible & status_eligible
