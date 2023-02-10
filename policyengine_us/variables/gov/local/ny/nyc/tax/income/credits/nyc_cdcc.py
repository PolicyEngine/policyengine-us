from policyengine_us.model_api import *
import numpy as np


class nyc_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf"
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # The NYC CDCC is a share of the NY State CDCC.
        # The share magnitude is determined by the fraction of CDCC
        # relevant expenses used for children under 4 and the NYC CDCC rate,
        # which depends on income.

        # First get their FAGI.
        fagi = tax_unit("adjusted_gross_income", period)

        # Then get the CDCC part of the parameter tree.
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.child_and_dependent_care_credit

        # Calculate eligibility.
        # Generally, one can claim the CDCC if they quality for the NYS CDCC
        # (which is generally based on qualifying for the federal CDCC).
        # They also need to have a FAGI <= $30k.
        eligible = fagi <= p.income_limit

        # Get their NY State CDCC (line 14 on Form IT-216).
        nys_cdcc = tax_unit("ny_cdcc", period)

        # Get the share of CDCC relevant expenses used for children under 4.
        cdcc_expenses = tax_unit(
            "cdcc_relevant_expenses", period
        )  # Line 3a on Form IT-216.
        cdcc_share_expenses_child_under_four = tax_unit(
            "cdcc_share_expenses_child_under_four", period
        )
        expenses_share_child_under_4 = (
            cdcc_expenses * cdcc_share_expenses_child_under_four
        )  # Line 23 on Form IT-216.

        # Take this share of the NY State CDCC.
        nyc_qualifying_cdcc_amount = nys_cdcc * expenses_share_child_under_4

        # Calculate the NYC CDCC rate which depends on income.
        cdcc_rate = p.rate.calc(fagi, right=True)

        return eligible * nyc_qualifying_cdcc_amount * cdcc_rate
