from policyengine_us.model_api import *


class ny_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pit/file/itemized-deductions.htm",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    pre-TCJA federal rules. Unlike federal rules post-2017, NY still
    allows casualty and theft loss deductions not limited to federally
    declared disasters. The 10% AGI floor still applies.
    """

    def formula(tax_unit, period, parameters):
        # NY uses pre-TCJA rules: casualty losses are still deductible
        # (not limited to federally declared disasters like federal post-2017)
        loss = add(tax_unit, period, ["casualty_loss"])
        p = parameters(period).gov.irs.deductions.itemized.casualty
        positive_agi = tax_unit("positive_agi", period)
        # Apply the 10% AGI floor (pre-TCJA rule)
        return max_(0, loss - positive_agi * p.floor)
