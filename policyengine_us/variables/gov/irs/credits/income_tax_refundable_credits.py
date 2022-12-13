from policyengine_us.model_api import *


class income_tax_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "refundable tax credits"
    documentation = "Total refundable income tax credits"
    unit = USD
    adds = [
        "eitc",
        "refundable_american_opportunity_credit",
        "refundable_ctc",
        "recovery_rebate_credit",
        "refundable_payroll_tax_credit",
        "premium_tax_credit",
        "ecpa_filer_credit",
        "ecpa_adult_dependent_credit",
    ]
