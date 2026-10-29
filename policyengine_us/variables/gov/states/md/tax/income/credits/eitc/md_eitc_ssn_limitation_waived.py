from policyengine_us.model_api import *


class md_eitc_ssn_limitation_waived(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maryland waives the EITC's Social Security number limitation"
    documentation = "Whether Maryland computes the federal credit its earned income credits start from without the IRC 32(m) Social Security number limitation. From 2020 it does for every return; unlike Maine, Maryland sets no federal filing condition."
    definition_period = YEAR
    reference = (
        # (c)(1)(i), (c)(2)(iii), (c)(3)(i)2 and (d) compute the § 32 credit
        # without regard to the limitation under § 32(m).
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#m",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        return parameters(period).gov.states.md.tax.income.credits.eitc.itin_eligible
