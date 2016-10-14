# coding: utf-8

# Import necessary packages
import os
from IPython.display import Image
from scipy import ndimage, misc
from six.moves import cPickle as pickle
import tensorflow as tf
import numpy as np

import scipy.io

from app import app
from flask import current_app

# We will use the pretrained 19-layer VGG model
def make_image(style_image_file, content_image_file, num_iterations):
    with app.app_context():
        TMP_DIR = current_app.config['INTERMEDIATE_IM_DIR']

    VGG_MODEL = 'imagenet-vgg-verydeep-19.mat'

    vgg = scipy.io.loadmat(VGG_MODEL)
    vgg_layers = vgg['layers']
    print('VGG model loaded')

    model = {}

    # dtype=[('name', 'O'), ('type', 'O'), ('weights', 'O'), ('size', 'O'), ('pad', 'O'), ('stride', 'O'), ('precious', 'O'), ('opts', 'O')]

    def weights_and_biases(layer_index):
        W = tf.constant(vgg_layers[0][layer_index][0][0][2][0][0])
        b = vgg_layers[0][layer_index][0][0][2][0][1]
        b = tf.constant(np.reshape(b, (b.size))) # need to reshape b from size (64,1) to (64,)
        layer_name = vgg_layers[0][layer_index][0][0][0][0]
        return W,b

    def build_graph(graph):
        nonlocal model
        with graph.as_default():
            model = {}
            model['input_image'] = tf.Variable(np.zeros((1, 224, 224, 3)), dtype = 'float32')
            W,b = weights_and_biases(0)
            model['conv1_1'] = tf.nn.conv2d(model['input_image'], W, [1,1,1,1], 'SAME') + b
            model['relu1_1'] = tf.nn.relu(model['conv1_1'])
            W,b = weights_and_biases(2)
            model['conv1_2'] = tf.nn.conv2d(model['relu1_1'], W, [1,1,1,1], 'SAME') + b
            model['relu1_2'] = tf.nn.relu(model['conv1_2'])
            model['pool1'] = tf.nn.avg_pool(model['relu1_2'], ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
            W,b = weights_and_biases(5)
            model['conv2_1'] = tf.nn.conv2d(model['pool1'], W, [1,1,1,1], 'SAME') + b
            model['relu2_1'] = tf.nn.relu(model['conv2_1'])
            W,b = weights_and_biases(7)
            model['conv2_2'] = tf.nn.conv2d(model['relu2_1'], W, [1,1,1,1], 'SAME') + b
            model['relu2_2'] = tf.nn.relu(model['conv2_2'])
            model['pool2'] = tf.nn.avg_pool(model['relu2_2'], ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
            W,b = weights_and_biases(10)
            model['conv3_1'] = tf.nn.conv2d(model['pool2'], W, [1,1,1,1], 'SAME') + b
            model['relu3_1'] = tf.nn.relu(model['conv3_1'])
            W,b = weights_and_biases(12)
            model['conv3_2'] = tf.nn.conv2d(model['relu3_1'], W, [1,1,1,1], 'SAME') + b
            model['relu3_2'] = tf.nn.relu(model['conv3_2'])
            W,b = weights_and_biases(14)
            model['conv3_3'] = tf.nn.conv2d(model['relu3_2'], W, [1,1,1,1], 'SAME') + b
            model['relu3_3'] = tf.nn.relu(model['conv3_3'])
            W,b = weights_and_biases(16)
            model['conv3_4'] = tf.nn.conv2d(model['relu3_3'], W, [1,1,1,1], 'SAME') + b
            model['relu3_4'] = tf.nn.relu(model['conv3_4'])
            model['pool3'] = tf.nn.avg_pool(model['relu3_4'], ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
            W,b = weights_and_biases(19)
            model['conv4_1'] = tf.nn.conv2d(model['pool3'], W, [1,1,1,1], 'SAME') + b
            model['relu4_1'] = tf.nn.relu(model['conv4_1'])
            W,b = weights_and_biases(21)
            model['conv4_2'] = tf.nn.conv2d(model['relu4_1'], W, [1,1,1,1], 'SAME') + b
            model['relu4_2'] = tf.nn.relu(model['conv4_2'])
            W,b = weights_and_biases(23)
            model['conv4_3'] = tf.nn.conv2d(model['relu4_2'], W, [1,1,1,1], 'SAME') + b
            model['relu4_3'] = tf.nn.relu(model['conv4_3'])
            W,b = weights_and_biases(25)
            model['conv4_4'] = tf.nn.conv2d(model['relu4_3'], W, [1,1,1,1], 'SAME') + b
            model['relu4_4'] = tf.nn.relu(model['conv4_4'])
            model['pool4'] = tf.nn.avg_pool(model['relu4_4'], ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
            W,b = weights_and_biases(28)
            model['conv5_1'] = tf.nn.conv2d(model['pool4'], W, [1,1,1,1], 'SAME') + b
            model['relu5_1'] = tf.nn.relu(model['conv5_1'])
            W,b = weights_and_biases(30)
            model['conv5_2'] = tf.nn.conv2d(model['relu5_1'], W, [1,1,1,1], 'SAME') + b
            model['relu5_2'] = tf.nn.relu(model['conv5_2'])
            W,b = weights_and_biases(32)
            model['conv5_3'] = tf.nn.conv2d(model['relu5_2'], W, [1,1,1,1], 'SAME') + b
            model['relu5_3'] = tf.nn.relu(model['conv5_3'])
            W,b = weights_and_biases(34)
            model['conv5_4'] = tf.nn.conv2d(model['relu5_3'], W, [1,1,1,1], 'SAME') + b
            model['relu5_4'] = tf.nn.relu(model['conv5_4'])
            model['pool5'] = tf.nn.avg_pool(model['relu5_4'], ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
            print('end of build graph function')

    def gram_matrix(F, N, M):
        # F is the output of the given convolutional layer on a particular input image
        # N is number of feature maps in the layer
        # M is the total number of entries in each filter
        Ft = tf.reshape(F, (M, N))
        return tf.matmul(tf.transpose(Ft), Ft)

    def loss_by_layer(a, x):
        N = a.shape[3]
        M = a.shape[1] * a.shape[2]
        A = gram_matrix(a, N, M)
        G = gram_matrix(x, N, M)
        loss = (1.0 / (4 * N**2 * M**2)) * tf.reduce_sum(tf.pow(G - A, 2))
        return loss

    def style_difference(session):
        # global model
        weights = [1.0, 1.0, 1.0, 1.0, 1.0]
        layer_losses = [loss_by_layer(session.run(model['relu' + str(i) + '_1']), model['relu' + str(i) + '_1']) for i in range(1, 6)] 
        return sum(layer_losses)

    def content_difference(session):
        content_loss = (2 * tf.nn.l2_loss(
            session.run(model['relu4_2']) - model['relu4_2']))
        return content_loss

    def generate_noise_image():
        return np.random.uniform(0, 256,(1, 224, 224, 3)).astype('float32')

    def get_imarray(im_file):
        array = ndimage.imread(im_file, mode='RGB')
        array = np.asarray([misc.imresize(array, (224, 224))])
        return array

    def write_image(path, image):
      image = image[0]
      image = np.clip(image, 0, 255).astype('uint8')
      scipy.misc.imsave(path, image)

    graph = tf.Graph()
    build_graph(graph)
    print('tf graph built')
    print(model)

    with tf.Session(graph=graph) as sess:
        
        # Load the images.
        style_image = get_imarray(style_image_file)
        content_image = get_imarray(content_image_file)

        noise_image = generate_noise_image()

        # Construct style_loss tensor using style_image.
        sess.run(tf.initialize_all_variables())
        sess.run(model['input_image'].assign(style_image))
        style_loss = style_difference(sess)
        print("style loss tensor created")

        # Construct content_loss tensor
        sess.run(tf.initialize_all_variables())
        sess.run(model['input_image'].assign(content_image))
        content_loss = content_difference(sess)
        # content_loss = 0
        print("content loss tensor created")

        total_loss = 100 * style_loss + 5 * content_loss

        optimizer = tf.train.AdamOptimizer(10)
        train_step = optimizer.minimize(total_loss)

        sess.run(tf.initialize_all_variables())
        sess.run(model['input_image'].assign(noise_image))
        for it in range(num_iterations):
            sess.run(train_step)
            print("Iteration: " + str(it))
            mixed_image = sess.run(model['input_image'])
            write_image(os.path.join(TMP_DIR, str(it) + '.png'), mixed_image)
            yield(str(it) + '.png')
        # clear out intermediate temporary images
        for im_file in os.listdir(TMP_DIR):
            if im_file != (str(num_iterations-1) + '.png'):
                os.remove(os.path.join(TMP_DIR, im_file))