from openfisca_us.model_api import *


class rptc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Refundable Payroll Tax Credit"
    documentation = "Refundable Payroll Tax Credit for filing unit"
    unit = USD


refundable_payroll_tax_credit = variable_alias(
    "refundable_payroll_tax_credit", rptc
)


class rptc_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Refundable Payroll Tax Credit for taxpayer"
    unit = USD


class rptc_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Refundable Payroll Tax Credit for spouse"
    unit = USD
