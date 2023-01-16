from typing import List
import itertools

from connector_sales_base import SaleEntry, Ticket
import tgbot.services.salary_calculator.salary_rates as salary_rates

ticket_prices = list(salary_rates.DISCOUNT_PRICE_COEFFICIENT.keys())


def entry_to_tickets(entry: SaleEntry) -> List[Ticket]:
    count = entry.count

    if count == 1:
        return [Ticket(green_id=entry.green_id, order_status=entry.order_status,
                       price=entry.full_sum, vr_code=entry.vr_code, sale_time=entry.sale_time)]

    # get all combinations of count prices
    ticket_combinations = list(itertools.combinations_with_replacement(ticket_prices, count))
    # create a map {ticket_price_sum: ticket_combination}
    sum_combinations = {sum(comb): comb for comb in ticket_combinations}
    prices = sum_combinations[entry.full_sum]

    return [Ticket(green_id=entry.green_id, order_status=entry.order_status, price=prices[i], vr_code=entry.vr_code,
                   sale_time=entry.sale_time) for i in range(count)]
