from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_inputs_available(Variable):
    """Legal facts and the full qualified payment total are available.

    Known ineligibility does not erase available facts. Known zero is distinct
    from a negative unknown sentinel; an unknown amount does not erase an
    independently established active election or its coordination restriction.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit monetary inputs are known"
    definition_period = YEAR
    defined_for = "wi_veterans_property_tax_credit_eligibility_available"
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 27-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        taxes = tax_unit(
            "wi_veterans_property_tax_credit_qualified_property_taxes", period
        )
        return taxes >= 0
