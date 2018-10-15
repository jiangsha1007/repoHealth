import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
if __name__ == '__main__':
    # 定义两个向量a,b
    a = tf.constant([1.0, 2.0], name='a')
    b = tf.constant([2.0, 3.0], name='b')
    result = a + b
    sess = tf.Session()  # 生成一个会话，通过一个会话session来计算结果
    # 实现了一个简单的Tensorflow模型
    print(sess.run(result))