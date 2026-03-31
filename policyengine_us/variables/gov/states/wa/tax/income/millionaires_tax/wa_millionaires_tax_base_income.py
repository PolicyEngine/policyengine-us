from policyengine_us.model_api import *


class wa_millionaires_tax_base_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax base income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=5",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=9",
    )
    defined_for = "wa_millionaires_tax_applies"
    documentation = """
    Washington base income is federal adjusted gross income as modified by
    Sections 302 through 308 and 401 through 407 of ESSB 6346.

    Key modifications include:
    - Long-term capital gains are replaced with Washington capital gains
      (as defined in RCW 82.87) to avoid double-taxation with the capital gains tax
    - Tax-exempt interest from non-WA state/local bonds is added back
    - State/local income taxes deducted federally are added back
    - Net operating loss carryovers from pre-2028 are not allowed

    This simplified implementation uses federal AGI as the base, with full
    Section 302-308 modifications deferred for future enhancement.
    """
    adds = ["adjusted_gross_income"]
