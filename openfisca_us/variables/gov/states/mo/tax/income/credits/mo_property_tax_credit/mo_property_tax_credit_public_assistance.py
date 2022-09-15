from openfisca_us.model_api import *


class mo_property_tax_credit_public_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit demographic eligiblity test"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # The second reference specifies that food stamps are not counted as income for this form.
        # Form also specifies that verterans payments and benefits are included unless an individual
        # is 100% disabled as a result of military service
        # fully_disabled_service_connected_veteran = person("is_fully_disabled_service_connected_veteran", period)
        # unclear if we currently model veterans benefits
        # tanf is currently not included in this formula, issue here: https://github.com/PolicyEngine/openfisca-us/issues/1361
        return add(tax_unit, period, ["ssi", "child_support_received"])
