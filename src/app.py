import streamlit as st
import numpy as np
import pandas as pd
from typing import Any, Tuple

KEY_CURRENT_BALANCE = "current_balance"
KEY_ANNUAL_WITHDRAWAL = "annual_withdrawal"
KEY_ANNUAL_DEPOSIT = "annual_deposit"
KEY_CURRENT_AGE = "current_age"
KEY_RETIREMENT_AGE = "retirement_age"
KEY_MARKET_CRASH_PERCENTAGE = "market_crash_percentage"
KEY_MARKET_CRASH_AGE = "market_crash_age"

STANDARD_DEVIATION = 0.03 # 3% (Market returns can deviate +/- 3% from mean value)
MEAN = 0.05 # 5% (Average annual return, but can fluctuate based on standard deviation)
SCENARIOS = 100000 # How many scenarios to calculate for one year returns
WITHDRAWAL_RATE_THRESHOLD = 0.15

def init_app():
    st.set_page_config(
        layout="wide",
        page_title="Monte Carlo Retirement Simulator"
    )

    st.title("Monte Carlo Retirement Simulator")
    st.subheader("Retirement fund simulation via Monte Carlo Random Algorithm")

    if KEY_CURRENT_BALANCE not in st.session_state:
        st.session_state[KEY_CURRENT_BALANCE] = 30000
    if KEY_ANNUAL_WITHDRAWAL not in st.session_state:
        st.session_state[KEY_ANNUAL_WITHDRAWAL] = 14000
    if KEY_ANNUAL_DEPOSIT not in st.session_state:
        st.session_state[KEY_ANNUAL_DEPOSIT] = 7000
    if KEY_CURRENT_AGE not in st.session_state:
        st.session_state[KEY_CURRENT_AGE] = 20
    if KEY_RETIREMENT_AGE not in st.session_state:
        st.session_state[KEY_RETIREMENT_AGE] = 55
    if KEY_MARKET_CRASH_PERCENTAGE not in st.session_state:
        st.session_state[KEY_MARKET_CRASH_PERCENTAGE] = 0
    if KEY_MARKET_CRASH_AGE not in st.session_state:
        st.session_state[KEY_MARKET_CRASH_AGE] = 0

def setup_inputs() -> Tuple[float, float, float, int, int, float, int]:
    current_balance = st.number_input(
        label="Current Balance",
        key=KEY_CURRENT_BALANCE,
        placeholder="Put an amount..."
    )

    annual_left, annual_right = st.columns(2)
    annual_withdrawal = annual_left.number_input(
        label="Annual Withdrawal",
        key=KEY_ANNUAL_WITHDRAWAL,
        placeholder="Put an amount..."
    )
    annual_deposit = annual_right.number_input(
        label="Annual Deposit",
        key=KEY_ANNUAL_DEPOSIT,
        placeholder="Put an amount..."
    )

    age_left, age_right = st.columns(2)
    current_age = age_left.number_input(
        label="Current Age",
        key=KEY_CURRENT_AGE,
        step=1,
        placeholder="Put an age..."
    )
    retirement_age = age_right.number_input(
        label="Retirement Age",
        key=KEY_RETIREMENT_AGE,
        step=1,
        placeholder="Put an age..."
    )

    market_crash_left, market_crash_right = st.columns(2)
    market_crash_percentage = market_crash_left.number_input(
        label="Market Crash Percentage",
        key=KEY_MARKET_CRASH_PERCENTAGE,
        placeholder="Crash market by.."
    )
    market_crash_age = market_crash_right.number_input(
        label="Market Crash Age",
        key=KEY_MARKET_CRASH_AGE,
        step=1,
        placeholder="Crash market at age of..."
    )

    return current_balance, annual_withdrawal, annual_deposit, current_age, retirement_age, market_crash_percentage, market_crash_age

def calculate_monte_carlo_matrix(stddev: float | np.ndarray, total_years: int) -> np.ndarray[Any, Any]:
    market_return_probabilities_matrix = np.random.normal(
        loc=MEAN,
        scale=stddev.reshape(-1, 1) if type(stddev) == np.ndarray else stddev,
        size=(total_years, SCENARIOS)
    )

    return market_return_probabilities_matrix

def get_summary_row(age, balances):
    return [
        age,
        balances.min(),
        np.percentile(balances, 25),
        np.median(balances),
        np.percentile(balances, 75),
        np.percentile(balances, 90),
        balances.max(),
        (balances > 0).mean() * 100
    ]

def calculate_all_years(current_balance: float, annual_withdrawal: float, annual_deposit: float, current_age: int, retirement_age: int, market_crash_percentage: float, market_crash_age: int) -> pd.DataFrame:
    results = pd.DataFrame(columns=["Age", "Worst", "25th", "Median", "75th", "90th", "Best", "Success"])
    total_steps = 100 - current_age
    market_crash_step = market_crash_age - current_age
    retirement_index = retirement_age - current_age
    last_balances = np.full(SCENARIOS, float(current_balance))
    results.loc[len(results)] = get_summary_row(current_age, last_balances)

    stddev_matrix = np.full(total_steps, STANDARD_DEVIATION)
    for i in range(0, 3):
        stddev_matrix[market_crash_step + i] = STANDARD_DEVIATION * 1.5
    stddev_matrix[retirement_index:] = STANDARD_DEVIATION * 0.6

    age_returns_matrix = calculate_monte_carlo_matrix(
        stddev=stddev_matrix,
        total_years=total_steps
    )

    for i in range(total_steps):
        age = current_age + 1 + i
        yearly_return = age_returns_matrix[i]

        if age >= retirement_age:
            last_balances = (last_balances * (1 + yearly_return)) - annual_withdrawal
        else:
            last_balances = (last_balances * (1 + yearly_return)) + annual_deposit

        last_balances = np.maximum(last_balances, 0)

        if age == market_crash_age:
            last_balances *= (1 - (market_crash_percentage / 100))

        results.loc[len(results)] = get_summary_row(age, last_balances)

    return results
    

def main():
    init_app()

    current_balance, annual_withdrawal, annual_deposit, current_age, retirement_age, market_crash_percentage, market_crash_age = setup_inputs()

    if st.button(
        label="Calculate",
        use_container_width=True
    ):
        if current_age >= retirement_age:
            st.write("Current Age cannot be equal nor greater than Retirement Age")
            return
        if market_crash_age < current_age:
            st.write("Market Crash was not applied due to it being set at a age lower than Current Age")

        simulated_balances = calculate_all_years(
            current_balance=current_balance,
            annual_withdrawal=annual_withdrawal,
            annual_deposit=annual_deposit,
            current_age=current_age,
            retirement_age=retirement_age,
            market_crash_percentage=market_crash_percentage,
            market_crash_age=market_crash_age
        )

        def style_rows(row, retirement_age):
            styles = ['' for _ in row.index]

            if row['Age'] == retirement_age:
                return ['background-color: blue; color: white; font-weight: bold' for _ in row.index]

            if row['Age'] >= retirement_age:
                cols_to_check = ["Worst", "25th", "Median", "75th", "90th", "Best"]
                
                for i, col_name in enumerate(row.index):
                    if col_name in cols_to_check:
                        val = row[col_name]
                        if val == 0:
                            styles[i] = 'background-color: red; color: white'
                        elif val * WITHDRAWAL_RATE_THRESHOLD <= annual_withdrawal:
                            styles[i] = 'color: red'
                        else:
                            styles[i] = 'color: white'
                            
            return styles

        styled_balances = simulated_balances.style.format({
            "Age": "{:.0f}",
            "Worst": "${:,.2f}",
            "25th": "${:,.2f}",
            "Median": "${:,.2f}",
            "75th": "${:,.2f}",
            "90th": "${:,.2f}",
            "Best": "${:,.2f}",
            "Success": "{:.2f}%"
        }).apply(
            func=style_rows,
            retirement_age=retirement_age,
            axis=1
        )

        st.dataframe(styled_balances, hide_index=True, use_container_width=True)



if __name__ == "__main__":
    main()