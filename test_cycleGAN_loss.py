import tensorflow as tf 
import numpy as np 
from glob import glob
from PIL import Image
import scipy.misc
import os 

"""
Import model definition
"""
from cycleGAN_loss import CycleGAN

"""
Function to load image from path and rescale it to [-1,1]. 
"""
def get_image_new(image_path,width,height):
    image = Image.open(image_path)
    image = image.resize([width,height],Image.BILINEAR)
    image = np.array(image,dtype=np.float32)
    image = np.divide(image,255)
    image = np.subtract(image,0.5)
    image = np.multiply(image,2)
    return image


"""
Function to test CycleGAN for test images. 
"""
def test(cgan_net,testA,testB,input_shape):
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        #change second argument to path where weights have been saved 
        saver.restore(sess,model_dir+"try_200\\")
        
        imgA = np.reshape(get_image_new(testA,input_shape[0],input_shape[1]),(1,input_shape[0],input_shape[1],input_shape[2]))
        imgB = np.reshape(get_image_new(testB,input_shape[0],input_shape[1]),(1,input_shape[0],input_shape[1],input_shape[2]))
        
        genA,genB,cycA,cycB = sess.run([cgan_net.gen_A,cgan_net.gen_B,cgan_net.cyclicA,cgan_net.cyclicB],
                                       feed_dict={cgan_net.input_A:imgA,cgan_net.input_B:imgB})
        images = [imgA,genA,cycA,imgB,genB,cycB]
        img_ind = 0 
        for img in images:
            img = np.reshape(img,input_shape)
            if np.array_equal(img.max(),img.min()) == False:
                img = (((img - img.min())*255)/(img.max()-img.min())).astype(np.uint8)
            else:
                img = ((img - img.min())*255).astype(np.uint8)
            scipy.misc.toimage(img, cmin=0.0, cmax=...).save(images_dir+"\\img_"+str(img_ind)+".jpg")
            img_ind = img_ind + 1
            

def main(_):
    if not os.path.exists(FLAGS.testA_image):
        print ("TestA image doesn't exist")
    else:
        if not os.path.exists(FLAGS.testB_image):
            print ("TestB image doesn't exist")
        else:
            if not os.path.exists(FLAGS.model_dir):
                print ("CycleGAN model is not available at the specified path")
            else:
                if not os.path.exists(FLAGS.images_dir):
                    os.makedirs(FLAGS.images_dir)
            
                input_shape = 128,128,3
                batch_size = 1
                pool_size = 50 
                beta1 = 0.5
                loss_type = FLAGS.loss_type
                tf.reset_default_graph()
                
                cgan_net = CycleGAN(batch_size,input_shape,pool_size,beta1,loss_type)
                test(cgan_net,FLAGS.testA_image,FLAGS.testB_image,FLAGS.model_dir,FLAGS.images_dir,input_shape)       


flags = tf.app.flags
flags.DEFINE_string("testA_image",None,"TestA Image Path")
flags.DEFINE_string("testB_image",None,"TestB Image Path")
flags.DEFINE_string("model_dir",None,"Path to checkpoint folder")
flags.DEFINE_string("images_dir","images_dir","Directory where images sampled from the generator (while testing the model) are stored")
flags.DEFINE_string("loss_type","l1","Loss type with which cycleGAN model is to be tested")
FLAGS = flags.FLAGS
    
if __name__ == '__main__':
    tf.app.run()
