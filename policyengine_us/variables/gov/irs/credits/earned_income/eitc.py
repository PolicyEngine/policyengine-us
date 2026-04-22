from policyengine_us.model_api import *


class eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Federal earned income credit"
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD
    defined_for = "eitc_eligible"

    def formula(tax_unit, period, parameters):
        takes_up_eitc = tax_unit("takes_up_eitc", period)
        maximum = tax_unit("eitc_maximum", period)
        phased_in = tax_unit("eitc_phased_in", period)
        reduction = tax_unit("eitc_reduction", period)
        limitation = max_(0, maximum - reduction)
        # EITC is claimed on a filed federal return (26 USC § 32, Form
        # 1040 with Schedule EIC). Non-filers receive $0. We cannot use
        # `tax_unit_is_filer` directly because it depends on
        # `eligible_for_refundable_credits`, which reads `eitc` — a
        # circular reference. Instead, compose the filer condition from
        # its non-circular inputs.
        is_required = tax_unit("tax_unit_is_required_to_file", period)
        files_voluntarily = tax_unit("would_file_taxes_voluntarily", period)
        would_file_for_credits = tax_unit(
            "would_file_if_eligible_for_refundable_credit", period
        )
        is_filer = is_required | files_voluntarily | would_file_for_credits
        return min_(phased_in, limitation) * takes_up_eitc * is_filer
