from policyengine_us.model_api import *


class pr_personal_property_casualty_loss_carryover(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico personal property casualty loss carried over"
    documentation = (
        "Personal property casualty loss from either of the two preceding "
        "taxable years that the filer may carry over to this year. Hacienda's "
        "instructions describe it as the part of the $5,000 ($2,500 if married "
        "filing separately) allowance not claimed in the year of the loss. "
        "It counts toward this year's annual cap."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # P.R. Internal Revenue Code of 2011, Section 1033.15(a)(10)(B)(i)
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=167",
        # 2025 Schedule A Individual, Part I, line 5
        "https://hacienda.pr.gov/sites/default/files/inst_individuals_2025.pdf#page=26",
    )
