from policyengine_us.model_api import *


class mi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan exemptions"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.exemptions

        # Personal Exemptions & Stillborn Exemptions
        personal_exemption = tax_unit("mi_personal_exemptions", period)

        # Disabled exemptions
        disabled_people = add(
            tax_unit, period, ["mi_disabled_exemption_eligible_person"]
        )
        disabled_exemption = disabled_people * p.disabled.amount.base

        # Disabled veteran exemptions
        disabled_veterans = add(
            tax_unit, period, ["is_fully_disabled_service_connected_veteran"]
        )
        disabled_veteran_exemption = (
            disabled_veterans * p.disabled.amount.veteran
        )

        # Dependent-on-other-return exemptions
        filing_status = tax_unit("filing_status", period)
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        dependent_exemption = (
            dependent_elsewhere * p.dependent_on_other_return[filing_status]
        )

        # Total exemptions
        return (
            where(dependent_elsewhere, dependent_exemption, personal_exemption)
            + disabled_exemption
            + disabled_veteran_exemption
        )
