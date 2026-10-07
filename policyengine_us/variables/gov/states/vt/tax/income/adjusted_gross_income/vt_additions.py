from policyengine_us.model_api import *


class vt_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont AGI additions"
    unit = USD
    documentation = "Additions to Vermont adjusted gross income"
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )

    def formula(tax_unit, period, parameters):
        # 32 V.S.A. 5811(21)(A)(i) adds the taxpayer's interest income from
        # non-Vermont state and local obligations excluded from federal
        # adjusted gross income. A tax unit dependent's interest is on the
        # dependent's own return, so only the head's and spouse's count.
        return tax_unit_non_dep_add(tax_unit, period, ["tax_exempt_interest_income"])
