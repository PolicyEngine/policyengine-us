from policyengine_us.model_api import *


class az_benefits_annuities_pensions_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona benefits, annuitites and pensions subtraction"
    unit = USD
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=15"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.deductions.benefits_annuities_pensions
        person = tax_unit.members

        filing_status = tax_unit("filing_status", period)
        married = filing_status == filing_status.possible_values.JOINT
        military_retirement_pay = min_(
            p.max_amount, person("military_retirement_pay", period)
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)

        subtraction_joint = tax_unit.sum(
            military_retirement_pay * (head + spouse)
        )

        subtraction_other = tax_unit.sum(military_retirement_pay * head)

        return where(married, subtraction_joint, subtraction_other)
