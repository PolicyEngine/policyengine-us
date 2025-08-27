# Test case: Should flag ALL these hard-coded values


class id_liheap_benefit(Variable):
    def formula(person, period, parameters):
        # BAD: Hard-coded base amount
        base_benefit = 500

        # BAD: Hard-coded percentage
        income = person("employment_income", period)
        if income < 1000:  # BAD: Hard-coded threshold
            multiplier = 0.5  # BAD: Hard-coded factor
        else:
            multiplier = 0.33  # BAD: Another hard-coded factor

        # BAD: Hard-coded months
        month = period.start.month
        if month in [10, 11, 12, 1, 2, 3]:  # BAD: Hard-coded season
            seasonal_bonus = 100  # BAD: Hard-coded bonus
        else:
            seasonal_bonus = 0

        # BAD: Hard-coded age threshold
        age = person("age", period)
        if age >= 60:  # BAD: Should be parameter
            elderly_bonus = 200  # BAD: Hard-coded amount
        else:
            elderly_bonus = 0

        return base_benefit * multiplier + seasonal_bonus + elderly_bonus


# Expected issues to find:
# 1. base_benefit = 500
# 2. income threshold 1000
# 3. multiplier 0.5
# 4. multiplier 0.33
# 5. months [10, 11, 12, 1, 2, 3]
# 6. seasonal_bonus = 100
# 7. age >= 60
# 8. elderly_bonus = 200
# Total: 8 hard-coded values
