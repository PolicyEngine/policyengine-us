from policyengine_us.model_api import *


class wi_property_tax_credit_rent_inputs_available(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin school credit rent heat classification is available"
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
        unclassified = (with_heat == -1) & (without_heat == -1)
        no_rent_to_classify = person("rent", period) == 0
        # This uses existing rent defaults; it does not verify zero expenses,
        # tenure, other eligibility facts or a complete tax return.
        return tax_unit.all(complete | (unclassified & no_rent_to_classify))
