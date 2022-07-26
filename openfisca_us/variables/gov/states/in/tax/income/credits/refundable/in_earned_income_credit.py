from openfisca_us.model_api import *


class in_earned_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN earned income credit"
    definition_period = YEAR
    documentation = "Indiana earned income credit amount calculated in 2021 as 9 percent of 2010 federal EIC and in 2022 as 10 percent."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3.1-21" 
    # use 2010 federal EITC when added later
