from policyengine_us.model_api import *


class tax_unit_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit Railroad Retirement social security equivalent benefits"
    unit = USD
    documentation = (
        "The members' social security equivalent benefits. As with reported "
        "Social Security benefits, each amount must be finite and "
        "nonnegative. When repayments exceed a year's benefits, box 5 of "
        "Form RRB-1099 shows a negative amount, which IRS Publication 915 "
        "offsets against the box 5 amounts on the filer's other forms and, "
        "on a joint return, the spouse's; the model doesn't net them."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#d_1_B",
        # Pub. 915 (2024), "Repayments More Than Gross Benefits", PDF page 15.
        "https://www.irs.gov/pub/irs-prior/p915--2024.pdf#page=15",
    )

    def formula(tax_unit, period, parameters):
        benefits = tax_unit.members(
            "railroad_social_security_equivalent_benefits", period
        )
        if np.any(~np.isfinite(benefits) | (benefits < 0)):
            raise ValueError(
                "railroad_social_security_equivalent_benefits must be finite "
                "and nonnegative, as reported Social Security benefits must be"
            )
        return tax_unit.sum(benefits)
