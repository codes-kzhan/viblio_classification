from viblio.common.utils import s3utils
from viblio.projects.video_download.mturk import mturkapi
from viblio.common import config
from configobj import ConfigObj
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

class Testmturkapi(unittest.TestCase):

    def setUp(self):
        s3conn = s3utils.S3()
        bucket_name='viblioclassification-test'
        image_path = config.resource_dir() + '/features/sample_img_001.jpg'
        image_s3_url=s3conn.upload(bucket_name,image_path,True)
        list_url=[]
        list_url.append(image_s3_url)
        mt_config = config.resource_dir() + '/projects/video_download/mturk_unittest_task.cfg'
        self.mt_params_config_file=config.resource_dir() + '/projects/video_download/mturk_unittest_params.cfg'
        self.mt =mturkapi.MTurkAPI(mt_config,'mechanicalturk.sandbox.amazonaws.com')
        self.url=image_s3_url
        self.listurl=list_url
        #print self.url
        
    def test_submit_and_parse(self):
        hitid = self.mt.sumbit_one(self.listurl,self.mt_params_config_file)
        #print "hittypeid: " +hitid.HITTypeId
        self.assertTrue(hitid.HITId,'No hit id returned')
        # Going to the web browser and submitting hit using selenium
        # This will openup firefox and submit hit as a worker
        hit_type_id=hitid.HITTypeId
        driver = webdriver.Firefox()
        driver.get("https://workersandbox.mturk.com")
        time.sleep(1)
        element = driver.find_element_by_id("lnkWorkerSignin").click()
        time.sleep(1)
        user=driver.find_element_by_name("email")
        pword = driver.find_element_by_name("password")
        user.send_keys("peebles@video-analytics-inc.com")
        pword.send_keys("Viblio2013")
        pword.send_keys(Keys.RETURN)
        time.sleep(1)
        driver.get("https://workersandbox.mturk.com/mturk/preview?groupId={hit_type_id}".format(**vars()))
        time.sleep(1)
        continue_work=driver.find_element_by_name("/accept").click()
        time.sleep(1)
        select=driver.find_element_by_name("Answer_1").click()
        time.sleep(1)
        finish=driver.find_element_by_name("/submit").click()
        time.sleep(2)
        driver.quit()
        time.sleep(10)

        #Testing parse function
        hit_id=hitid.HITId
        #print "Hitid: "+hit_id
        out=self.mt.parse(hit_id)
        #print out
        for x in out:
            self.assertTrue(x[0].strip()==self.url,'Returned url from parse doesnt match')
            
        
        self.mt.delete_hit(hit_id)
        time.sleep(6)

if __name__=='__main__':
    unittest.main()
