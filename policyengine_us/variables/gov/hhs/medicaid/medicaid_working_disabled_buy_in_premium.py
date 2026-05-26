from policyengine_us.model_api import *


class medicaid_working_disabled_buy_in_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid working disabled Buy-In annual premium"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dhcs.ca.gov/services/working-disabled-program/",
        "https://hfs.illinois.gov/medicalprograms/hbwd/premiums.html",
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
    )

    def formula(tax_unit, period, parameters):
        monthly_premiums = tax_unit.members(
            "medicaid_working_disabled_buy_in_premium_person",
            period.first_month,
        )
        return tax_unit.sum(monthly_premiums) * MONTHS_IN_YEAR
