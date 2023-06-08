from policyengine_us.model_api import *


class mi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Exemptions"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.exemptions

        # Personal Exemptions
        person = tax_unit("tax_unit_size", period)
        personal_exemption = person * p.amount

        # Dependent exemptions
        dependent = tax_unit("tax_unit_dependents", period)
        dependent_exemption = dependent * p.dependent_amount

        # Stillborn Exemptions
        stillborn = tax_unit("tax_unit_stillborn_parent", period).astype(int)
        stillborn_exemption = stillborn * p.special_exemptions.stillborn_amount

        # Disabled exemptions
        disabled = tax_unit("head_is_disabled", period)
        disabled_exemption = disabled * p.special_exemptions.disabled_amount

        # Disabled veteran exemptions
        disabled_veteran = tax_unit("tax_unit_disabled_veteran", period)
        disabled_veteran_exemption = (
            disabled_veteran * p.special_exemptions.disabled_veteran_amount
        )

        # Is dependent exemptions
        filing_status = tax_unit("filing_status", period)
        is_dependent = tax_unit("tax_unit_is_dependent", period).astype(int)
        is_dependent_exemption = (
            is_dependent
            * p.special_exemptions.is_dependent_amount[filing_status]
        )

        # Total exemptions
        return (
            personal_exemption
            + dependent_exemption
            + stillborn_exemption
            + disabled_exemption
            + disabled_veteran_exemption
            + is_dependent_exemption
        )
