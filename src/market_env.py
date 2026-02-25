import random
import math

class MarketEnv:
    def __init__(self, initial_price=100.0, volatility=0.02, num_agents=2, max_steps=1000):
        self.initial_price = initial_price
        self.volatility = volatility
        self.num_agents = num_agents
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.price = self.initial_price
        self.steps = 0
        self.inventories = [0] * self.num_agents
        self.cash = [1000.0] * self.num_agents  # Start with 1000 cash
        self.signals = [0] * self.num_agents # 0: Neutral, 1: Buy Intention, 2: Sell Intention
        self.price_history = [self.price]
        return self._get_state()

    def _get_state(self):
        # State is simply the current price (normalized) and relative time
        # For simplicity, we return a dictionary
        hist = self.price_history[-10:]
        if len(hist) < 10:
            hist = [self.price] * (10 - len(hist)) + hist

        return {
            'price': self.price,
            'price_history': hist,
            'inventories': list(self.inventories),
            'cash': list(self.cash),
            'signals': list(self.signals),
            'step': self.steps
        }

    def step(self, actions_with_signals):
        """
        Executes one step in the environment.
        actions_with_signals: list of tuples (action, signal) for each agent.
                              action: 0: Hold, 1: Buy, 2: Sell
                              signal: 0: Neutral, 1: Bullish, 2: Bearish
        """
        self.steps += 1

        actions = [a[0] for a in actions_with_signals]
        signals = [a[1] for a in actions_with_signals]
        self.signals = signals

        # calculate net demand
        buy_orders = sum([1 for a in actions if a == 1])
        sell_orders = sum([1 for a in actions if a == 2])
        net_demand = buy_orders - sell_orders

        # Price impact + Random Walk
        # Price Impact: Each net buy pushes price up by 1%, sell pushes down 1%
        price_impact = net_demand * 0.01
        random_shock = random.gauss(0, self.volatility)

        # Update price
        prev_price = self.price
        self.price = self.price * (1 + price_impact + random_shock)
        self.price = max(0.01, self.price) # Ensure positive price
        self.price_history.append(self.price)

        rewards = []
        info = {'actions': actions, 'price': self.price}

        # Process trades
        for i, action in enumerate(actions):
            reward = 0
            portfolio_val_before = self.cash[i] + self.inventories[i] * prev_price

            if action == 1: # Buy
                cost = prev_price
                if self.cash[i] >= cost:
                    self.cash[i] -= cost
                    self.inventories[i] += 1
            elif action == 2: # Sell
                if self.inventories[i] > 0:
                    revenue = prev_price
                    self.cash[i] += revenue
                    self.inventories[i] -= 1

            # Calculate new portfolio value
            portfolio_val_after = self.cash[i] + self.inventories[i] * self.price

            # Reward is the change in portfolio value (profit/loss)
            reward = portfolio_val_after - portfolio_val_before
            rewards.append(reward)

        done = self.steps >= self.max_steps

        return self._get_state(), rewards, done, info
