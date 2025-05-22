from policyengine_us.model_api import *


label = "Income"


class employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.employment_income"


class self_employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "self-employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"


class employment_income(Variable):
    value_type = float
    entity = Person
    label = "employment income"
    documentation = "Wages and salaries, including tips and commissions."
    unit = USD
    definition_period = YEAR
    adds = [
        "employment_income_before_lsr",
        "employment_income_behavioral_response",
    ]
    uprating = "calibration.gov.irs.soi.employment_income"


class self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "self-employment income"
    unit = USD
    documentation = "Self-employment non-farm income."
    definition_period = YEAR
    adds = [
        "self_employment_income_before_lsr",
        "self_employment_income_behavioral_response",
    ]
    uprating = "calibration.gov.irs.soi.self_employment_income"


class emp_self_emp_ratio(Variable):
    value_type = float
    entity = Person
    label = "employment-to-self-employment income ratio"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        earnings = employment_income + self_employment_income
        res = np.ones_like(earnings)
        mask = earnings > 0
        res[mask] = employment_income[mask] / earnings[mask]
        return res


class farm_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income averaging for farmers and fishermen. Schedule J. Seperate from QBI and self-employment income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_income"


class farm_operations_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income from active farming operations. Schedule F. Do not include this income in self-employment income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_income"  # TODO: update


class farm_rental_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Schedule E farm rental income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_income"  # TODO: update


class s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "S Corp Income"
    unit = USD
    documentation = "S Corporation active passthrough income. Schedule E. Do not include this income in self-employment income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"  # TODO: Update


class partnership_income(Variable):
    value_type = float
    entity = Person
    label = "Partnership Income"
    unit = USD
    documentation = "S Corporation active passthrough income. Schedule E. Do not include this income in self-employment income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"  # TODO: Update


class reit_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "REIT Dividend Income"
    unit = USD
    documentation = "REIT Dividend Income. Included in QBID."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"  # TODO: Update


class ptp_income(Variable):
    value_type = float
    entity = Person
    label = "Publically Traded Partnership Income"
    unit = USD
    documentation = "Publically Traded Partnership Income. Included in QBID."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"  # TODO: Update


class bdc_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Business Development Company Dividend Income"
    unit = USD
    documentation = " Business Development Company Dividend Income. Included in QBID."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"  # TODO: Update
