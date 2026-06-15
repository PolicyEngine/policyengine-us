from policyengine_us.model_api import *


class ca_marin_general_relief_gross_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Gross income counted under the Marin County General Relief"
    definition_period = YEAR
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11"

    adds = "gov.local.ca.marin.general_relief.income_sources"
