from typing import Tuple
from math import fsum, ceil
from .salary_rates import *
from tgbot.interfaces.connector_sales_base import *


# returns list of sales (considering tickets' price coefficients) by day
def apply_coefficient(tickets: List[List[Ticket]]) -> List[float]:
    sales_number = []
    for i, day in enumerate(tickets):
        sales_number.append(0)
        for ticket in day:
            if ticket.price <= 900:
                sales_number[i] += PRICE_COEFFICIENT[900]
            elif ticket.price <= 1750:
                sales_number[i] += PRICE_COEFFICIENT[1750]
            elif ticket.price <= 2600:
                sales_number[i] += PRICE_COEFFICIENT[2600]
            elif ticket.price <= 3500:
                sales_number[i] += PRICE_COEFFICIENT[3500]
            else:
                raise Exception

    return sales_number


# returns manager's week salary & today's salary
def manager_salary(tickets: List[List[Ticket]], is_regional: bool) -> Tuple[float, float]:
    if is_regional:
        manager_weekly_sales = REGIONAL_MANAGER_WEEKLY_SALES
        manager_ticket_payments = REGIONAL_MANAGER_TICKET_PAYMENTS
        manager_set_salary = REGIONAL_MANAGER_SET_SALARY
    else:
        manager_weekly_sales = REGULAR_MANAGER_WEEKLY_SALES
        manager_ticket_payments = REGULAR_MANAGER_TICKET_PAYMENTS
        manager_set_salary = REGULAR_MANAGER_SET_SALARY

    sales_number = apply_coefficient(tickets)  # sales*coefficients by day
    sales_number_today = sales_number[-1]  # last day (today) sales*coefficients

    # calculate manager's week salary depending on sum of sales in a week (rounding UP to 2 decimals)
    sales_sum = fsum(sales_number)

    if sales_sum > manager_weekly_sales['rate4']:
        week_salary = ceil(sales_sum * manager_ticket_payments['rate4'] * 100) / 100
        today_salary = ceil(sales_number_today * manager_ticket_payments['rate4'] * 100) / 100
    elif sales_sum > manager_weekly_sales['rate3']:
        week_salary = ceil(sales_sum * manager_ticket_payments['rate3'] * 100) / 100
        today_salary = ceil(sales_number_today * manager_ticket_payments['rate3'] * 100) / 100
    elif sales_sum > manager_weekly_sales['rate2']:
        week_salary = ceil(sales_sum * manager_ticket_payments['rate2'] * 100) / 100
        today_salary = ceil(sales_number_today * manager_ticket_payments['rate2'] * 100) / 100
    elif sales_sum > manager_weekly_sales['rate1']:
        week_salary = ceil(sales_sum * manager_ticket_payments['rate1'] * 100) / 100
        today_salary = ceil(sales_number_today * manager_ticket_payments['rate1'] * 100) / 100
    else:
        week_salary = manager_set_salary
        today_salary = ceil(sales_number_today * manager_ticket_payments['rate0'] * 100) / 100

    return week_salary, today_salary


def manager_week_salary(tickets: List[List[Ticket]], is_regional: bool) -> float:
    return manager_salary(tickets, is_regional)[0]


def manager_day_salary(tickets: List[List[Ticket]], is_regional: bool) -> float:
    return manager_salary(tickets, is_regional)[1]


# returns agent's week salary & today's salary
def agent_salary(tickets: List[List[Ticket]], is_regional: bool, is_new: bool, is_manager: bool) -> Tuple[float, float]:
    sales_number = apply_coefficient(tickets)  # sales*coefficients by day
    sales_number_today = sales_number[-1]  # last day (today) sales*coefficients

    # calculate agent's level depending on sum of sales in a week
    sales_sum = fsum(sales_number)
    if is_new:
        if is_regional:
            if is_manager:
                agent_ticket_payments = REGIONAL_AGENT_MANAGER_TICKET_PAYMENTS
            else:
                if sales_sum >= WEEKLY_SALES['lvl99']:
                    agent_ticket_payments = REGIONAL_AGENT_LVL99_TICKET_PAYMENTS
                elif sales_sum >= WEEKLY_SALES['lvl50']:
                    agent_ticket_payments = REGIONAL_AGENT_LVL50_TICKET_PAYMENTS
                else:
                    agent_ticket_payments = REGIONAL_AGENT_LVL15_TICKET_PAYMENTS
        else:
            if is_manager:
                agent_ticket_payments = REGULAR_AGENT_MANAGER_TICKET_PAYMENTS
            else:
                if sales_sum >= WEEKLY_SALES['lvl99']:
                    agent_ticket_payments = REGULAR_AGENT_LVL99_TICKET_PAYMENTS
                elif sales_sum >= WEEKLY_SALES['lvl50']:
                    agent_ticket_payments = REGULAR_AGENT_LVL50_TICKET_PAYMENTS
                else:
                    agent_ticket_payments = REGULAR_AGENT_LVL15_TICKET_PAYMENTS
    else:
        if is_manager:
            raise Exception
        if is_regional:
            raise Exception
        else:
            if sales_sum >= WEEKLY_SALES['lvl99']:
                agent_ticket_payments = OLDER_AGENT_LVL99_TICKET_PAYMENTS
            elif sales_sum >= WEEKLY_SALES['lvl50']:
                agent_ticket_payments = OLDER_AGENT_LVL50_TICKET_PAYMENTS
            else:
                agent_ticket_payments = OLDER_AGENT_LVL15_TICKET_PAYMENTS

    # calculate & return manager as agent week salary, today salary
    if is_manager:
        week_salary = 0
        for day in sales_number:
            if day >= AGENT_MANAGER_RATES['rate1']:
                week_salary += ceil(day * agent_ticket_payments['rate1'] * 100) / 100
            else:
                week_salary += ceil(day * agent_ticket_payments['rate0'] * 100) / 100

        if sales_number_today >= AGENT_MANAGER_RATES['rate1']:
            today_salary = ceil(sales_number_today * agent_ticket_payments['rate1'] * 100) / 100
        else:
            today_salary = ceil(sales_number_today * agent_ticket_payments['rate0'] * 100) / 100

        return week_salary, today_salary

    # calculate agent's rate depending on min sales for day in a week (rounding UP to 2 decimals)
    min_sales = min(sales_number)

    if min_sales >= AGENT_RATES['rate2']:
        week_salary = ceil(sales_sum * agent_ticket_payments['rate2'] * 100) / 100
        today_salary = ceil(sales_number_today * agent_ticket_payments['rate2'] * 100) / 100
    elif min_sales < AGENT_RATES['rate1']:
        week_salary = ceil(sales_sum * agent_ticket_payments['rate0'] * 100) / 100
        today_salary = ceil(sales_number_today * agent_ticket_payments['rate0'] * 100) / 100
    else:
        week_salary = ceil(sales_sum * agent_ticket_payments['rate1'] * 100) / 100
        today_salary = ceil(sales_number_today * agent_ticket_payments['rate1'] * 100) / 100

    return week_salary, today_salary


def agent_week_salary(tickets: List[List[Ticket]], is_regional: bool, is_new: bool, is_manager: bool) -> float:
    return agent_salary(tickets, is_regional, is_new, is_manager)[0]


def agent_day_salary(tickets: List[List[Ticket]], is_regional: bool, is_new: bool, is_manager: bool) -> float:
    return agent_salary(tickets, is_regional, is_new, is_manager)[1]
