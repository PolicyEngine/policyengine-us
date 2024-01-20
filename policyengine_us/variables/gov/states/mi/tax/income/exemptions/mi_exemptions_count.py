from policyengine_us.model_api import *


class mi_exemptions_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan exemptions count"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
        "https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf",
        "https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/BOOK_MI-1040CR-7.pdf#page=7",
    )

    def formula(tax_unit, period):
        # Personal Exemptions
        personal_count = add(tax_unit, period, ["is_tax_unit_head_or_spouse"])

        # Disabled
        disabled_count = add(
            tax_unit, period, ["mi_disabled_exemption_eligible_person"]
        )

        # Disabled veteran exemptions
        disabled_veterans_count = add(
            tax_unit, period, ["is_fully_disabled_service_connected_veteran"]
        )

        # Child & Dependent adult
        dependent_count = tax_unit("tax_unit_dependents", period)

        return (
            personal_count
            + disabled_count
            + disabled_veterans_count
            + dependent_count
        )
