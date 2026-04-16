import jsonpickle
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        try:
            price_history = jsonpickle.decode(state.traderData) if state.traderData else {}
        except:
            price_history = {}

        result = {}
        limits = {"ASH_COATED_OSMIUM": 80, "INTARIAN_PEPPER_ROOT": 80}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            current_pos = state.position.get(product, 0)
            limit = limits.get(product, 80)
            orders: List[Order] = []

            if not order_depth.buy_orders or not order_depth.sell_orders:
                continue

            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())

            # End of day safety: Flatten position to reduce risk
            if state.timestamp > 990000:
                if current_pos > 0: orders.append(Order(product, best_bid, -current_pos))
                elif current_pos < 0: orders.append(Order(product, best_ask, -current_pos))
                result[product] = orders
                continue

            if product == "ASH_COATED_OSMIUM":
                fair_price = 10000 
                buy_p, sell_p = fair_price - 7, fair_price + 7
                if current_pos < limit:
                    orders.append(Order(product, buy_p, limit - current_pos))
                if current_pos > -limit:
                    orders.append(Order(product, sell_p, -(limit + current_pos)))

            if product == "INTARIAN_PEPPER_ROOT":
                mid = (best_bid + best_ask) / 2
                if product not in price_history: price_history[product] = []
                history = price_history[product]
                history.append(mid)
                if len(history) > 20: history.pop(0)

                if len(history) >= 10:
                    fair_val = sum(history) / len(history)
                    # Symmetric threshold of 1 (The 124k version logic)
                    if best_ask < fair_val - 1 and current_pos < limit:
                        orders.append(Order(product, best_ask, limit - current_pos))
                    elif best_bid > fair_val + 1 and current_pos > -limit:
                        orders.append(Order(product, best_bid, -(limit + current_pos)))

            result[product] = orders

        return result, 0, jsonpickle.encode(price_history)