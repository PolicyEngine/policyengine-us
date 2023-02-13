from policyengine_us.model_api import *
import numpy as np


class nyc_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf"
    defined_for = "nyc_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        # The NYC CDCC is a share of the NY State CDCC.
        # The share magnitude is determined by the fraction of CDCC
        # relevant expenses used for children under 4 and the NYC CDCC rate,
        # which depends on income.

        # Get their NY State CDCC (line 14 on Form IT-216).
        nys_cdcc = tax_unit("ny_cdcc", period)

        # Get the share of CDCC relevant expenses used for children under 4.
        share_of_childcare_expenses_for_children_under_four = tax_unit(
            "share_of_childcare_expenses_for_children_under_four", period
        )

        # Take this share of the NY State CDCC.
        nyc_qualifying_cdcc_amount = (
            nys_cdcc * share_of_childcare_expenses_for_children_under_four
        )

        # Get the CDCC rate "applicable percentage" portion of the NYS CDCC
        applicable_percentage = tax_unit(
            "nyc_cdcc_applicable_percentage", period
        )

        return nyc_qualifying_cdcc_amount * applicable_percentage
