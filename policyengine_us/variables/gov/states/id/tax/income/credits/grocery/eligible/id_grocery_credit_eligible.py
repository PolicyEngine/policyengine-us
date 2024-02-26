from policyengine_us.model_api import *


class id_grocery_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Idaho grocery credit"
    definition_period = MONTH
    defined_for = StateCode.ID
    reference = (
        "https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
    )

    def formula(person, period, parameters):
        # Incarcerated people are not eligible for the grocery credit
        spm_unit = person.spm_unit
        snap_received = spm_unit("snap", period) > 0
        return ~person("is_incarcerated", period) & ~snap_received
