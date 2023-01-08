from typing import List, Tuple
from salary_rates import *  # reconsider


def manager_salary(sales_number: List[int], is_regional: bool) -> Tuple[float, float]:
    if is_regional:
        manager_weekly_sales = REGIONAL_MANAGER_WEEKLY_SALES
        manager_ticket_prices = REGIONAL_MANAGER_TICKET_PRICES
        manager_set_salary = REGIONAL_MANAGER_SET_SALARY
    else:
        manager_weekly_sales = REGULAR_MANAGER_WEEKLY_SALES
        manager_ticket_prices = REGULAR_MANAGER_TICKET_PRICES
        manager_set_salary = REGULAR_MANAGER_SET_SALARY

    sales_sum = sum(sales_number[:])

    if sales_sum > manager_weekly_sales['rate4']:
        return sales_sum * manager_ticket_prices['rate4'], sales_number[-1] * manager_ticket_prices['rate4']
    if sales_sum > manager_weekly_sales['rate3']:
        return sales_sum * manager_ticket_prices['rate3'], sales_number[-1] * manager_ticket_prices['rate3']
    if sales_sum > manager_weekly_sales['rate2']:
        return sales_sum * manager_ticket_prices['rate2'], sales_number[-1] * manager_ticket_prices['rate2']
    if sales_sum > manager_weekly_sales['rate1']:
        return sales_sum * manager_ticket_prices['rate1'], sales_number[-1] * manager_ticket_prices['rate1']
    return manager_set_salary, manager_set_salary / len(sales_number)  # divide by len or by 7?


def manager_week_salary(sales_number: List[int], is_regional: bool) -> float:
    return manager_salary(sales_number, is_regional)[0]


def manager_day_salary(sales_number: List[int], is_regional: bool) -> float:
    return manager_salary(sales_number, is_regional)[1]


def agent_salary(sales_number: List[int], is_regional: bool, is_new: bool) -> Tuple[float, float]:
    sales_sum = sum(sales_number[:])

    if is_new:
        if is_regional:
            if sales_sum >= WEEKLY_SALES['lvl99']:
                agent_ticket_prices = REGIONAL_AGENT_LVL99_TICKET_PRICES
            elif sales_sum >= WEEKLY_SALES['lvl50']:
                agent_ticket_prices = REGIONAL_AGENT_LVL50_TICKET_PRICES
            else:
                agent_ticket_prices = REGIONAL_AGENT_LVL15_TICKET_PRICES
        else:
            if sales_sum >= WEEKLY_SALES['lvl99']:
                agent_ticket_prices = REGULAR_AGENT_LVL99_TICKET_PRICES
            elif sales_sum >= WEEKLY_SALES['lvl50']:
                agent_ticket_prices = REGULAR_AGENT_LVL50_TICKET_PRICES
            else:
                agent_ticket_prices = REGULAR_AGENT_LVL15_TICKET_PRICES
    else:
        if is_regional:
            raise Exception
        else:
            if sales_sum >= WEEKLY_SALES['lvl99']:
                agent_ticket_prices = OLDER_AGENT_LVL99_TICKET_PRICES
            elif sales_sum >= WEEKLY_SALES['lvl50']:
                agent_ticket_prices = OLDER_AGENT_LVL50_TICKET_PRICES
            else:
                agent_ticket_prices = OLDER_AGENT_LVL15_TICKET_PRICES

    every_day_sales = []

    for n in sales_number:
        if n >= AGENT_RATES['rate2']:
            every_day_sales.append(n * agent_ticket_prices['rate2'])
        elif n < AGENT_RATES['rate1']:
            every_day_sales.append(n * agent_ticket_prices['rate0'])
        else:
            every_day_sales.append(n * agent_ticket_prices['rate1'])

    return sum(every_day_sales), every_day_sales[-1]


def agent_week_salary(sales_number: List[int], is_regional: bool, is_new: bool) -> float:
    return agent_salary(sales_number, is_regional, is_new)[0]


def agent_day_salary(sales_number: List[int], is_regional: bool, is_new: bool) -> float:
    return agent_salary(sales_number, is_regional, is_new)[1]
