import pandas as pd
import tensorflow as tf


class Network(object):
    def __init__(self, n_inputs, n_outputs, input_dtype, output_dtype, seed=None):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.input_dtype = input_dtype
        self.output_dtype = output_dtype
        self.seed = None

        self.data_placeholder = tf.placeholder(dtype=input_dtype, shape=[None, n_inputs], name='Input_data')
        self.target_placeholder = tf.placeholder(dtype=output_dtype, shape=[None, n_outputs], name='Target_data')
        self.layers_output = pd.Series([])
        self.Ws = pd.Series([])
        self.bs = pd.Series([])
        self.last_layer_neurons = n_inputs
        self.last_layer_inputs = self.data_placeholder

    def add_hidden_layer(self, n_neurons, activator=None):
        """
        W shape(n_last_layer_neurons, n_this_layer_neurons]
        b shape(n_this_layer_neurons, ]
        product = tf.matmul(x, W) + b
        :param n_neurons:
        :param activator:
        :return:
        """
        W = tf.Variable(tf.random_normal([self.last_layer_neurons, n_neurons],
                                         mean=0.0, stddev=0.3, dtype=self.input_dtype,
                                         seed=self.seed, name='weights'))
        b = tf.Variable(tf.random_uniform([n_neurons, ], minval=0, maxval=0.1,
                                          dtype=self.input_dtype, seed=self.seed, name='biases'))
        product = tf.matmul(self.last_layer_inputs, W, name='feed_product') + b

        if activator is None:
            activated_product = product
        else:
            activated_product = activator(product)
        self.last_layer_inputs = activated_product
        self.Ws.set_value(label=len(self.Ws), value=W)
        self.bs.set_value(label=len(self.bs), value=b)
        self.layers_output.set_value(label=len(self.layers_output),
                                     value=activated_product)
        self.last_layer_neurons = n_neurons

    def set_optimizer(self, optimizer, global_step=None):
        self._add_output_layer()
        self._init_loss()
        self.train_op = optimizer.minimize(self.loss, global_step)
        _init = tf.initialize_all_variables()
        self.sess = tf.Session()
        self.sess.run(_init)

    def run_step(self, feed_xs, feed_ys):
        self.sess.run(self.train_op, feed_dict={self.data_placeholder: feed_xs,
                                                self.target_placeholder: feed_ys})

    def get_loss(self, xs, ys):
        _loss_value = self.sess.run(self.loss,
                                    feed_dict={self.data_placeholder: xs,
                                               self.target_placeholder: ys})
        return _loss_value

    def get_weights(self, layer=None):
        if not(layer is None or type(layer) is int):
            raise TypeError('layer need to be None or int')
        if layer is None:
            Ws = []
            for W_layer in self.Ws:
                W = self.sess.run(W_layer)
                Ws.append(W)
        else:
            if layer >= len(self.Ws):
                raise IndexError('Do not have layer %i' % layer)
            Ws = self.sess.run(self.Ws[layer])
        return Ws

    def _add_output_layer(self):
        self.add_hidden_layer(self.n_outputs, activator=None)

    def _init_loss(self):
        self.loss = None