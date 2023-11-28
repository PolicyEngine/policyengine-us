from policyengine_us.model_api import *


class dependent_care_employer_benefits(Variable):
    value_type = float
    entity = Person
    label = "Dependent care benefits received from an employer"
    # description = "Amounts you received as an employee should be shown in Box 10 of your federal Form(s) W-2. If you were self-employed or a partner, include amounts you received under a dependent care assistance program from your sole proprietorship or partnership"
    unit = USD
    definition_period = YEAR
