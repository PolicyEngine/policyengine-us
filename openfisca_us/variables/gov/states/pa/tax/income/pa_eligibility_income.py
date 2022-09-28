from openfisca_us.model_api import *

<<<<<<< HEAD
=======
# calculated by subtracting the resident credit, which is currently not modeled

>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131

class pa_eligibility_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA eligibility income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40sp.pdf"
    defined_for = StateCode.PA
<<<<<<< HEAD
=======

    formula = sum_of_variables(["pa_total_taxable_income"])
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
