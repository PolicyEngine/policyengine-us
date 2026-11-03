from policyengine_us.model_api import *


class standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # IRC 63(c)(1) (the sum) and 63(c)(6)(A) (zero for a separate filer
        # whose spouse itemizes).
        "https://www.law.cornell.edu/uscode/text/26/63#c",
    )

    def formula(tax_unit, period, parameters):
        total = add(
            tax_unit,
            period,
            [
                "basic_standard_deduction",
                "additional_standard_deduction",
                "bonus_guaranteed_deduction",
            ],
        )
        # IRC 63(c)(6)(A): a married individual filing separately whose
        # spouse itemizes has a standard deduction of zero. The standard
        # deduction is the sum in 63(c)(1), so the additional amount for
        # age or blindness (63(c)(3), (f)) is zeroed as well, not only the
        # basic amount.
        filing_status = tax_unit("filing_status", period)
        separate_filer_itemizes = tax_unit("separate_filer_itemizes", period)
        return where(
            separate_filer_itemizes
            & (filing_status == filing_status.possible_values.SEPARATE),
            0,
            total,
        )
