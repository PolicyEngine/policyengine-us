from policyengine_us.model_api import *


class pr_principal_residence_casualty_loss(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico casualty loss on the principal residence"
    documentation = (
        "Loss on the real property that was the taxpayer's principal residence "
        "when the event occurred, caused by fire, hurricane, earthquake, storm, "
        "tropical depression, flood or another casualty, and not compensated by "
        "insurance or otherwise. Enter the loss once, on the head or spouse; a "
        "spouse filing a separate return enters the couple's whole loss."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # P.R. Internal Revenue Code of 2011, Section 1033.15(a)(10)(A)(i)
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=167",
        # 2025 Schedule A Individual, Part I, line 2
        "https://hacienda.pr.gov/sites/default/files/inst_individuals_2025.pdf#page=24",
    )
