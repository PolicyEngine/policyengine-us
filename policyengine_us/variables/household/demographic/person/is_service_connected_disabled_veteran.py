from policyengine_us.model_api import *


class is_service_connected_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Is a veteran with a service-connected disability, at any VA rating"
    documentation = (
        "Whether the person is a veteran with a disability incurred or "
        "aggravated in the line of duty in the active military, naval, air, "
        "or space service (38 U.S.C. 101(16)), whatever rating the Department "
        "of Veterans Affairs gives it, including 0%. A 100% rating also has "
        "its own input, is_fully_disabled_service_connected_veteran, which "
        "does not set this one, so a program that covers every rating reads "
        "both. Setting this input does not set is_veteran, which follows "
        "veterans_benefits. The model has no discharge input: each program "
        "that reads this input takes the veteran to have the discharge it "
        "requires."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/38/101#16"
