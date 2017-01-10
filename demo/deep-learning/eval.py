#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN
from tensorflow.contrib import learn

# Parameters
# ==================================================

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_dir", "", "Checkpoint directory from training run")
tf.flags.DEFINE_boolean("eval_train", False, "Evaluate on all training data")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")


FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")

# CHANGE THIS: Load data. Load your own data here
print("Loading data...")
x_test, y_test, vocabulary, vocabulary_inv = data_helpers.load_data(False)
positive_size = len(data_helpers.positive_examples)
negative_size = len(data_helpers.negative_examples)


y_test = np.argmax(y_test, axis=1)
print("x_test", len(x_test), x_test)
print("y_test", len(y_test), y_test)
print("\nEvaluating...\n")

# Evaluation
# ==================================================
checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name("output/predictions").outputs[0]

        # Generate batches for one epoch
        batches = data_helpers.batch_iter(list(x_test), FLAGS.batch_size, 1, shuffle=False)

        # Collect the predictions here
        all_predictions = []

        for x_test_batch in batches:
            batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
            all_predictions = np.concatenate([all_predictions, batch_predictions])

# Print accuracy if y_test is defined
if y_test is not None:


    with open('test_result.txt', 'w') as the_file:
      #for y in y_test:
      count = 0
      for p in all_predictions:
        #the_file.write(str(y)+"\r\n")
        count += 1
        if count > positive_size:
          the_file.write("neg-" + str(count - positive_size) + "\t" + str(p) + "\r\n")
        else:
          the_file.write("pos-" + str(count) + "\t" + str(p)+"\r\n")




    print("x_test len = ", len(x_test))
    print("y_test = ", y_test)
    correct_predictions = float(sum(all_predictions == y_test))
    print("Total number of test examples: {}".format(len(y_test)))
    print("Accuracy: {:g}".format(correct_predictions/float(len(y_test))))
    # print("Predictions", all_predictions)
    all_predictions = all_predictions.astype(np.float32, copy=False)
    y_test = y_test.astype(np.float32, copy=False)
    auc = tf.contrib.metrics.streaming_auc(all_predictions, y_test)
    sess = tf.Session()
    sess.run(tf.initialize_all_variables())
    sess.run(tf.initialize_local_variables())  # try commenting this line and you'll get the error
    train_auc = sess.run(auc)
    print("AUC: {:s}".format(train_auc))
