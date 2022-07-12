from openfisca_us.model_api import *


class md_aged_blind_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD aged blind exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"

    formula = sum_of_variables(
        [
            "md_aged_dependent_exemption",
            "md_aged_exemption",
            "md_blind_exemption",
        ]
    )
