from policyengine_us.model_api import *


class az_benefits_annuities_pensions_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona benefits, annuitites and pensions subtraction"
    unit = USD
    documentation = ""
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.deductions.benefits_annuities_pensions
        person = tax_unit.members

        filing_status = tax_unit("filing_status", period)
        married = filing_status == filing_status.possible_values.JOINT
        subtraction_amount = min_(
            p.amount, person("military_retirement_pay", period)
        )

        subtraction_joint = tax_unit.sum(subtraction_amount)

        head = person("is_tax_unit_head", period)
        subtraction_head = tax_unit.sum(subtraction_amount * head)

        return where(married, subtraction_joint, subtraction_head)
