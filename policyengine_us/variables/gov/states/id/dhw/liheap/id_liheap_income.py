from policyengine_us.model_api import *


class id_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP countable income"
    unit = USD
    definition_period = YEAR
    reference = "https://healthandwelfare.idaho.gov/services-programs/financial-assistance/home-heating-and-utility-assistance/"
    documentation = "Gross income for all household members used to determine LIHEAP eligibility"

    def formula(spm_unit, period, parameters):
        # LIHEAP uses gross income for eligibility determination
        # This is the same as SPM unit gross income
        return spm_unit("spm_unit_gross_income", period)