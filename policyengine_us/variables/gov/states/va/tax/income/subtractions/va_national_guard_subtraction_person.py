from policyengine_us.model_api import *


class va_national_guard_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia National Guard pay subtraction for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.national_guard_pay
        # Each filer's own pay up to the per-person cap, as in
        # va_national_guard_subtraction, sets the shares of the unit amount,
        # so a supplied unit amount is allocated too. A tax unit dependent's
        # pay is on the dependent's own return; with no filer pay, the head
        # takes a supplied amount.
        head_or_spouse = ~person("is_tax_unit_dependent", period)
        capped_pay = min_(
            person("military_service_income", period) * head_or_spouse, p.cap
        )
        total_capped_pay = person.tax_unit.sum(capped_pay)
        share = where(
            total_capped_pay > 0,
            np.divide(
                capped_pay,
                total_capped_pay,
                out=np.zeros_like(capped_pay),
                where=total_capped_pay > 0,
            ),
            person("is_tax_unit_head", period),
        )
        return person.tax_unit("va_national_guard_subtraction", period) * share
