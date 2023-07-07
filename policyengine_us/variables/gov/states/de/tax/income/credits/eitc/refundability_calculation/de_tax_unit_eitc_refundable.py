from policyengine_us.model_api import *


class de_tax_unit_eitc_refundable(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Delaware refundable earned income tax credit"
    unit = USD
    documentation = "Whether tax unit selects the refundable or non-refundable earned income tax credit."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if parameters(
            period
        ).simulation.de.branch_to_determine_if_refundable_eitc:
            # determine federal itemization behavior by comparing tax liability
            de_tax_liability_if_refundable_eitc = tax_unit(
                "de_tax_liability_if_refundable_eitc", period
            )
            de_tax_liability_if_non_refundable_eitc = tax_unit(
                "de_tax_liability_if_non_refundable_eitc", period
            )
            return (
                de_tax_liability_if_refundable_eitc
                < de_tax_liability_if_non_refundable_eitc
            )
        else:
            de_tax_liability_if_refundable_eitc = tax_unit(
                "de_tax_liability_if_refundable_eitc", period
            )
            de_tax_liability_if_non_refundable_eitc = tax_unit(
                "de_tax_liability_if_non_refundable_eitc", period
            )
            return (
                de_tax_liability_if_refundable_eitc
                >= de_tax_liability_if_non_refundable_eitc
            )
