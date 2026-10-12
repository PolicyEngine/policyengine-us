from policyengine_us.model_api import *


class assigned_ca_premium_subsidy(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned California Premium Subsidy for tax unit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        # Take-up-gated California Premium Subsidy, parallel to
        # assigned_aca_ptc. Program Design (a)/(c)(1) condition the benefit on
        # Covered California Exchange enrollment, which take-up captures.
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=1",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=100805.",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("ca_premium_subsidy", period) * tax_unit(
            "takes_up_ca_premium_subsidy_if_eligible", period
        )
