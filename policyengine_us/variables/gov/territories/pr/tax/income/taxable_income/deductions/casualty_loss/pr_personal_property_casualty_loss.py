from policyengine_us.model_api import *


class pr_personal_property_casualty_loss(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico casualty loss on automobiles and household goods"
    documentation = (
        "Loss on automobiles, furniture, fixtures and other household goods, "
        "excluding jewelry and cash, caused by an earthquake, hurricane, storm, "
        "tropical depression or flood in an area the Governor of Puerto Rico "
        "designated a disaster area, where the taxpayer claimed the disaster "
        "assistance benefits, and not compensated by insurance or otherwise. "
        "Enter the loss once, on the head or spouse; a spouse filing a separate "
        "return enters the couple's whole loss."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # P.R. Internal Revenue Code of 2011, Section 1033.15(a)(10)(B)
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=167",
        # 2025 Schedule A Individual, Part I, line 5
        "https://hacienda.pr.gov/sites/default/files/inst_individuals_2025.pdf#page=26",
    )
