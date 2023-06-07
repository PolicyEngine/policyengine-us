from policyengine_us.model_api import *


class mi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MI Exemptions"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.exemptions

        # Personal Exemptions
        person = tax_unit("person_count", period)
        personal_exemption = person * p.amount

        # Dependent exemptions
        dependent = tax_unit("dependent_count", period)
        dependent_exemption = dependent * p.dependent_amount

        # Stillborn Exemptions
        stillborn = tax_unit("stillborn_parent", period).astype(int)
        stillborn_exemption = stillborn * p.special_exemptions.stillborn_amount

        # Disabled exemptions
        disabled = tax_unit("disabled_count", period)
        disabled_exemption = disabled * p.special_exemptions.disabled_amount

        # Disabled veteran exemptions
        disabled_veteran = tax_unit("disabled_veteran_count", period)
        disabled_veteran_exemption = disabled_veteran * p.special_exemptions.disabled_veteran_amount

        # Total exemptions
        return personal_exemption + dependent_exemption + stillborn_exemption + disabled_exemption + disabled_veteran_exemption
