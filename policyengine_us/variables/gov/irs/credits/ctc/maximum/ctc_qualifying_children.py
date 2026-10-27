from policyengine_us.model_api import *


class ctc_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "CTC-qualifying children"
    documentation = (
        "Count of children for whom the filer can claim the Child Tax Credit. "
        "Children whose filer fails the identification requirements of IRC "
        "24(e)(2) or 24(h)(7)(A)(i) are not counted."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#c",
        "https://www.law.cornell.edu/uscode/text/26/24#h_7",
    )

    adds = ["ctc_qualifying_child"]
