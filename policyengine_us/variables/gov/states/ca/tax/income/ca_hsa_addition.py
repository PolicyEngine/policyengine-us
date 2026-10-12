from policyengine_us.model_api import *


class ca_hsa_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "California HSA addition"
    documentation = (
        "Health Savings Account contributions federally excluded from AGI but "
        "added back for California income tax."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-1005-publication.pdf#page=10"

    def formula(tax_unit, period, parameters):
        payroll_contributions = add(
            tax_unit, period, ["health_savings_account_payroll_contributions"]
        )
        return payroll_contributions + tax_unit("health_savings_account_ald", period)
