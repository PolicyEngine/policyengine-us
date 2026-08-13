from policyengine_us.model_api import *


class ca_sbd_general_relief_gross_earned_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "San Bernardino County General Relief gross earned income"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx"

    adds = "gov.local.ca.sbd.general_relief.income.sources.earned"
