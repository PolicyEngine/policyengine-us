from policyengine_us.model_api import *


class wi_property_tax_credit_rent_constituting_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rent constituting property taxes for the Wisconsin school credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    reference = (
        "https://docs.legis.wisconsin.gov/2021/statutes/statutes/71.pdf#page=48",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=18",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        with_heat = person("wi_property_tax_credit_rent_with_heat", period)
        without_heat = person("wi_property_tax_credit_rent_without_heat", period)
        complete = (with_heat >= 0) & (without_heat >= 0)
        p = parameters(period).gov.states.wi.tax.income.credits.property_tax
        classified = (
            max_(with_heat, 0) * p.rent_fraction
            + max_(without_heat, 0) * p.rent_fraction_without_heat
        )
        # Unclassified rent retains the existing approximation; availability is
        # reported separately rather than interpreting missing heat facts as zero.
        legacy = person("rent", period) * p.rent_fraction
        return tax_unit.sum(where(complete, classified, legacy))
