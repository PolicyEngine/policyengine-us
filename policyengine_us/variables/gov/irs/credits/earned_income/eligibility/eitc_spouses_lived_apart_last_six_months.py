from policyengine_us.model_api import *


class eitc_spouses_lived_apart_last_six_months(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Spouses had different principal residences for the last six months"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#d_2_B_iii_I"
    documentation = """
    Whether the filer and spouse had different principal places of abode
    throughout the last six months of the tax year, for the separated-spouse
    exception in IRC 32(d)(2)(B)(iii)(I). Defaults to true when the tax unit
    head or spouse is separated (is_separated), the model's existing
    living-apart indicator, which the head-of-household, filing-status and
    child and dependent care credit rules also read. Set this input directly
    to override the default. It does not establish the legal-separation
    route in IRC 32(d)(2)(B)(iii)(II), which requires a separation
    instrument and separate households at year end.
    """

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        return tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("is_separated", period)
        )
