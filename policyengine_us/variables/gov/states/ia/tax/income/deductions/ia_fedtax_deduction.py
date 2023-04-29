from policyengine_us.model_api import *


class ia_fedtax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa deduction for selected components of federal income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=41"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=41"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # Iowa allows a deduction of federal income taxes from Iowa net
        # income, but federal payroll taxes (FICA and SECA and Additional
        # Medicare) cannot be used to reduced Iowa net income.
        setax = add(tax_unit, period, ["self_employment_tax"])
        amtax = tax_unit("additional_medicare_tax", period)
        net_income_additions = setax + amtax
        # federal income taxes are before refundable federal credits
        gross_ded = tax_unit("income_tax_before_refundable_credits", period)
        return gross_ded - net_income_additions
