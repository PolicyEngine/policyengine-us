from openfisca_us.model_api import *


class standard(Variable):
    value_type = float
    entity = TaxUnit
    label = "Standard deduction (zero for itemizers)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        # Calculate basic standard deduction
        basic_stded = tax_unit("basic_standard_deduction", period)
        filing_status = tax_unit("filing_status", period)
        separate_filer_itemizes = tax_unit("separate_filer_itemizes", period)
        filing_statuses = filing_status.possible_values

        # Calculate extra standard deduction for aged and blind
        extra_stded = tax_unit("aged_blind_extra_standard_deduction", period)

        # Calculate the total standard deduction.
        initial_standard = basic_stded + extra_stded
        # Separate filers get zero if their spouse itemizes.
        return where(
            (filing_status == filing_statuses.SEPARATE)
            & separate_filer_itemizes,
            0,
            initial_standard,
        )
