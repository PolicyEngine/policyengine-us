from policyengine_us.model_api import *


class oh_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.70",
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=24",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=18",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.deductions.plan_529_contributions
        contribution_amount = tax_unit_non_dep_add(
            tax_unit, period, ["investment_in_529_plan_indv"]
        )
        beneficiaries = tax_unit_non_dep_add(
            tax_unit, period, ["count_529_contribution_beneficiaries"]
        )
        cap = p.cap * beneficiaries
        return min_(contribution_amount, cap)
