import tensorflow as tf
from ...agent import Agent
from ...loop import Loop
from ....environment import Environment
from .replay import ExperienceReplay
from .prioritized_replay import PrioritizedExperienceReplay
from .network import Network
from ...Utilities.lr_scheduler import LRScheduler
from typing import Dict

class DDQN(Agent):

      def __init__(self, env: Environment, **hyperparams) -> None:
          self._env = env
          self._alias = 'ddqn'
          self._observe = hyperparams.get('observe', 5000)
          self._explore = hyperparams.get('explore', 10000)
          self._batch_size = hyperparams.get('batch_size', 32)
          self._replay_limit = hyperparams.get('replay_limit', 10000)
          self._epsilon_range = hyperparams.get('epsilon_range', (1, 0.0001))
          self._training_interval = hyperparams.get('training_interval', 5)
          self._target_frequency = hyperparams.get('target_frequency', 3000)
          self._network = hyperparams.get('network', 'dueling')
          self._replay_type = hyperparams.get('replay', 'prioritized')
          self._decay_type = hyperparams.get('decay_type', 'linear')
          self._gamma = hyperparams.get('gamma', 0.9)
          self._alpha = hyperparams.get('alpha', 0.7)
          self._beta = hyperparams.get('beta', 0.5)
          self._replay = ExperienceReplay(self._replay_limit,
                                          self._batch_size) if replay_type == 'regular' else PrioritizedExperienceReplay(self._alpha,
                                                                                                                         self._beta,
                                                                                                                         self._replay_limit,
                                                                                                                         self._batch_size)
          self._lr = hyperparams.get('learning_rate', 0.0001)
          self._lr_scheduler_scheme = hyperparams.get('lr_scheduler_scheme', 'linear')
          self._lr_scheduler = LRScheduler(self._lr_scheduler_scheme, self._lr)
          self._session = self._build_network_graph(hyperparams)
          self._q_update_session = self._build_td_update_graph()
          self._mutate_alias(self._alias)

      def __repr__(self) -> str:
          return self._alias

      def _mutate_alias(self, alias: str, hyperparams: Dict) -> str:
          components = 2
          extended_alias = '' 
          if hyperparams.get("n_step", None):
             extended_alias += "NStep"
             components += 1
          if hyperparams.get("distributional", None):
             extended_alias += "Distributional"
             components += 1
          if hyperparams.get("noisy", None):
             extended_alias += "Noisy"
             components += 1
          if hyperparams["replay"] == "prioritized":
             extended_alias += "Prioritized"
             components += 1
          if hyperparams["network"] == "dueling":
             extended_alias += "Dueling"
             components += 1
          else:
             if hyperparams["network"] == "rnn"
                extended_alias += "Recurrent"
          alias = extended_alias + alias if components < 7 else "RAINBOW"
          return alias

      def _build_network_graph(self) -> tf.Session:
          graph = tf.Graph()
          session = tf.Session(graph=graph)
          with graph.as_default():
               optional_network_params = self._get_optional_network_params(hyperparams)
               self._local_network = getattr(Network, self._network)(self._env.state.size, self._env.action.size,
                                                                     optional_network_params, 'local')
               self._target_network = getattr(Network, self._network)(self._env.state.size, self._env.action.size,
                                                                      optional_network_params, 'target')
          return session

      def _build_td_update_graph(self) -> tf.Session:
          graph = tf.Graph()
          session = tf.Session(graph=graph)
          with graph.as_default():
               with tf.device('/cpu:0'):
                    self._q_values = tf.placeholder(shape=[None, self._action_size], dtype=tf.float32)
                    self._q_values_next = tf.placeholder(shape=[None, self._action_size], dtype=tf.float32)
                    self._q_values_next_target = tf.placeholder(shape=[None, self._action_size], dtype=tf.float32)
                    self._actions = tf.placeholder(shape=[None], dtype=tf.int32)
                    self._rewards = tf.placeholder(shape=[None], dtype=tf.float32)
                    self._terminated = tf.placeholder(shape=[None], dtype=tf.bool)
                    filter_tensor = tf.tile(tf.expand_dims(self._terminated, axis=1), [1, self._action_size])
                    mask_tensor = tf.one_hot(indices=self._actions, depth=self._action_size)
                    reward_masked = mask_tensor * tf.expand_dims(self._rewards, axis=1)
                    q_masked_inverted = tf.cast(tf.equal(mask_tensor, 0), tf.float32) * self._q_values
                    q_next_mask = tf.one_hot(indices=tf.argmax(self._q_values_next, axis=1), depth=self._action_size)
                    updated_q_vals = self._rewards + self._gamma * tf.reduce_sum(q_next_mask * self._q_values_next_target, axis=1)
                    updated_q_vals_masked = mask_tensor * tf.expand_dims(updated_q_vals, axis=1)
                    self._updated_q_values = tf.where(filter_tensor, q_masked_inverted + reward_masked, q_masked_inverted + updated_q_vals_masked)
          return session

      def _get_optional_network_params(self, hyperparams: Dict) -> Dict:
          optional_network_params = ['gradient_network_params']
          params_dict = dict()
          for param in optional_network_params:
              if hyperparams.get(param, None):
                 params_dict[param] = hyperparams[param]
          return params_dict
          