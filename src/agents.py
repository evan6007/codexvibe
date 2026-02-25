import random
import math

class Agent:
    def __init__(self, agent_id):
        self.agent_id = agent_id

    def act(self, state):
        raise NotImplementedError

    def learn(self, state, action, reward, next_state):
        pass

class QLearningAgent(Agent):
    def __init__(self, agent_id, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(agent_id)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.actions = [(a, s) for a in [0, 1, 2] for s in [0, 1, 2]] # 9 combined actions

    def _discretize_state(self, state):
        """Convert continuous state into a discrete tuple for Q-table."""
        price_history = state['price_history']
        current_price = state['price']

        # 1. Price Trend
        if len(price_history) < 2:
            trend = 0 # Flat
        else:
            prev_price = price_history[-2]
            if current_price > prev_price * 1.01:
                trend = 1 # Up
            elif current_price < prev_price * 0.99:
                trend = -1 # Down
            else:
                trend = 0 # Flat

        # 2. Inventory Level
        inventory = state['inventories'][self.agent_id]
        if inventory <= 0:
            inv_level = 0
        elif inventory < 5:
            inv_level = 1
        else:
            inv_level = 2

        # 3. Aggregated Signal from Others
        signals = state.get('signals', [])
        other_signals = [s for i, s in enumerate(signals) if i != self.agent_id]
        if not other_signals:
            avg_signal = 0
        else:
            # simple majority vote
            counts = {0:0, 1:0, 2:0}
            for s in other_signals:
                counts[s] += 1
            avg_signal = max(counts, key=counts.get)

        return (trend, inv_level, avg_signal)

    def get_q(self, state, action_idx):
        return self.q_table.get((state, action_idx), 0.0)

    def act(self, state):
        discrete_state = self._discretize_state(state)

        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            action_idx = random.randrange(len(self.actions))
        else:
            q_values = [self.get_q(discrete_state, i) for i in range(len(self.actions))]
            max_q = max(q_values)
            # Handle ties randomly
            best_indices = [i for i, q in enumerate(q_values) if q == max_q]
            action_idx = random.choice(best_indices)

        return self.actions[action_idx]

    def learn(self, state, action, reward, next_state):
        # Q-learning update rule
        # Note: 'action' here is the tuple (trade, signal), we need its index
        try:
            action_idx = self.actions.index(action)
        except ValueError:
            return # Should not happen

        discrete_state = self._discretize_state(state)
        discrete_next_state = self._discretize_state(next_state)

        current_q = self.get_q(discrete_state, action_idx)
        max_next_q = max([self.get_q(discrete_next_state, i) for i in range(len(self.actions))])

        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(discrete_state, action_idx)] = new_q
