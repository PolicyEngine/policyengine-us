from openfisca_us.model_api import *


class mo_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # Check demographic eligibility
        demographic_qualification = tax_unit(
            "mo_property_tax_credit_demographic_tests", period
        )
        # Check for housing expense eligibility

        any_housing_cost = tax_unit("pays_property_tax_or_rent", period)
        # Check demographic eligibility.
        credit = tax_unit("mo_property_tax_credit_amount", period)
        return demographic_qualification * any_housing_cost * credit
