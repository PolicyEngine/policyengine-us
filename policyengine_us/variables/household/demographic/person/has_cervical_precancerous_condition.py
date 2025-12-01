from policyengine_us.model_api import *


class has_cervical_precancerous_condition(Variable):
    value_type = bool
    entity = Person
    label = "Has cervical precancerous condition"
    documentation = "Whether the person has been diagnosed with a cervical precancerous condition, such as Cervical Intraepithelial Neoplasia grade III (CIN III), severe cervical dysplasia, High-Grade Squamous Intraepithelial Lesion (HGSIL), or Atypical Glandular Cells (AGC) with adenocarcinoma suspicion."
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=33528"
