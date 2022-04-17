# -*- coding: utf-8 -*-
import csv

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import random
import time


class QccSpider(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.index = 0

    def openQcc(self):
        """打开企查查"""
        self.driver.get('https://www.qcc.com/')
        time.sleep(random.randrange(2, 5))
        # 点击登录按钮
        self.driver.find_element_by_xpath('//ul[@class="navbar-nav"]/li[11]/a/span').click()
        time.sleep(random.randrange(2, 5))
        # 点击其他登录方式
        self.driver.find_element_by_xpath('//*[@id="loginModal"]/div/div/div/div[2]/div[2]/div/div[1]/a').click()
        time.sleep(random.randrange(2, 5))
        # 点击QQ快速登录
        self.driver.find_element_by_xpath('//*[@id="loginModal"]/div/div/div/div[2]/div[2]/div/div[1]/a[2]').click()
        time.sleep(random.randrange(2, 5))
        # 进入iframe框架
        self.driver.switch_to.frame('ptlogin_iframe')
        # 有时候xpath定位不到iframe里面的标签可以用css
        self.driver.find_element_by_xpath('//*[@id="img_out_1347337893"]').click()
        time.sleep(random.randrange(4, 6))
        self.searchBrand()

    def searchBrand(self):
        """搜索商标"""
        # 在搜索框中输入阿里
        self.driver.find_element_by_xpath('//div[@class="form-group"]/div[@class="input-group"]/input').send_keys('阿里')
        time.sleep(random.randrange(2, 5))
        # 点击查一下按钮进行搜索
        self.driver.find_element_by_xpath('//div[@class="form-group"]/div[@class="input-group"]/span/button').click()
        time.sleep(random.randrange(2, 5))
        # 点击综合
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[1]/a').click()
        time.sleep(random.randrange(2, 5))
        # 点击查看全部结果按钮
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/a').click()
        time.sleep(random.randrange(2, 5))
        # 获取商标详情信息页面
        self.getBrand()

    def getBrand(self):
        """获取商标详情信息页面"""
        # 商标对象列表
        brandList = self.driver.find_elements_by_xpath('//div/table[@class="ntable ntable-list"]/tr/td[2]/div/div/a')
        for i in range(len(brandList)):
            if i > 3:
                break
            # 点击商标对象进入详情页提取
            time.sleep(random.randrange(2, 5))
            brandList[i].click()
            time.sleep(random.randrange(2, 5))
            self.getBrandInfo()

    def getBrandInfo(self):
        """获取商标详情信息"""
        winHandles = self.driver.window_handles
        self.driver.switch_to.window(winHandles[1])
        time.sleep(random.randrange(2, 5))
        # 申请进度标题
        scheduleTitle = self.driver.find_element_by_xpath \
            ('/html/body/div[1]/div[2]/div[2]/div[1]/section/div/div[1]/div/h3').text
        # 申请进度状态,相邻两个为一组(需要遍历提取出来，与基本信息一样)
        scheduleStates = self.driver.find_elements_by_xpath('//div[@class="text"]')
        scheduleStatesList = self.getBrandList(scheduleStates)
        scheduleStatesList = self.stringConvert(scheduleStatesList, "-", ".")
        print('申请进度标题', scheduleTitle, "申请进度状态", scheduleStatesList)
        # 商标基本信息对象列表
        brandObjectList = self.driver.find_elements_by_xpath('//div[@class="sub-part"]/table/tr/td')
        # 遍历商标基本信息对象列表提取商标基本信息
        brandInfoList = self.getBrandList(brandObjectList)
        brandInfoList = self.stringConvert(brandInfoList, "-", ".")
        print("商标基本信息", brandInfoList)
        # 商标流程状态时间
        brandStatusTimes = self.driver.find_elements_by_xpath('//div[@class="e_history"]/div/div/div/div[1]')
        brandStatusTimesList = self.getBrandList(brandStatusTimes)
        brandStatusTimesList = self.stringConvert(brandStatusTimesList, '\n', " ")
        # 商标流程状态申请返回内容
        brandStatusContent = self.driver.find_elements_by_xpath('//div[@class="e_history"]/div/div/div/div[2]')
        brandStatusContentList = self.getBrandList(brandStatusContent)
        print("商标流程状态时间", brandStatusTimesList, "商标流程状态申请返回内容", brandStatusContentList)
        # 进入联系方式页面获取联系方式
        connectMannerList = self.getConnectManner()
        # 将所有信息整合保存
        brandInfoList.append(scheduleTitle)
        brandInfoList.append(scheduleStatesList)
        brandInfoList.append('商标流程状态时间')
        brandInfoList.append(brandStatusTimesList)
        brandInfoList.append('商标流程状态申请返回内容')
        brandInfoList.append(brandStatusContentList)
        brandInfoList.append("联系方式")
        brandInfoList.append(connectMannerList)
        print('整合后的数据', brandInfoList)
        self.saveCsv(brandInfoList)
        # 关闭当前窗口
        self.driver.close()
        winHandles = self.driver.window_handles
        self.driver.switch_to.window(winHandles[0])

    def saveCsv(self, saveList):
        """
        存入csv文件
        :param saveList: 要保存的列表
        :return: None
        """
        titleBrand = []
        contentBrand = []
        self.index += 1
        with open('qcc.csv', 'a', newline='') as f:
            write = csv.writer(f)
            for i in range(len(saveList)):
                if i % 2 == 0:
                    titleBrand.append(saveList[i])
                else:
                    contentBrand.append(saveList[i])
            # 标题只写如一次
            if self.index == 1:
                write.writerow(titleBrand)
            write.writerow(contentBrand)

    def getBrandList(self, brand_list):
        """
        获取传入列表的文本内容text
        :param brand_list: 传入一个列表
        :return: 返回取出信息的列表
        """
        brandList = []
        for info in brand_list:
            brandList.append(info.text)
        return brandList

    def stringConvert(self, stringList, oldSting, newString):
        """
        用于将列表内的字符进行替换
        :param stringList: 传入的字符串列表
        :param oldSting: 需要替换的字符
        :param newString: 替换后字符
        :return: 替换字符后的字符串列表
        """
        for i in range(len(stringList)):
            stringList[i] = stringList[i].replace(oldSting, newString)
        return stringList

    def getConnectManner(self):
        """
        获取联系方式
        :return: 返回联系方式列表
        """
        self.driver.find_element_by_xpath \
            ('/html/body/div[1]/div[2]/div[2]/div[1]/section/div/div[2]/div[4]/table/tr[1]/td[2]/span/a').click()
        time.sleep(random.randrange(2, 5))
        winHandles = self.driver.window_handles
        self.driver.switch_to.window(winHandles[2])
        # 电话和邮箱的联系方式
        connectManner = self.driver.find_elements_by_xpath('//div[@class="rline"]/span[1]/span')
        connectMannerList = self.getBrandList(connectManner)
        print("联系方式", connectMannerList)
        time.sleep(random.randrange(2, 5))
        # 关闭当前窗口, 需要切换到前一个窗口
        self.driver.close()
        winHandles = self.driver.window_handles
        self.driver.switch_to.window(winHandles[1])
        return connectMannerList


if __name__ == "__main__":
    qcc = QccSpider()
    qcc.openQcc()

"""
登录按钮：//ul[@class="navbar-nav"]/li[11]/a/span
其他登录方式：//*[@id="loginModal"]/div/div/div/div[2]/div[2]/div/div[1]/a
QQ快捷登录：//*[@id="loginModal"]/div/div/div/div[2]/div[2]/div/div[1]/a[2]
QQ登录头像按钮(和权大师一样，需要先进入iframe框架): //*[@id="img_out_1347337893"]
搜索框：//div[@class="form-group"]/div[@class="input-group"]/input
查一下按钮：//div[@class="form-group"]/div[@class="input-group"]/span/button
查看所有搜索结果：/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/a
查找商标名称(点击该名称可以进入详情页面)：//div/table[@class="ntable ntable-list"]/tr/td[2]/div/div/a

商标申请进度名称：/html/body/div[1]/div[2]/div[2]/div[1]/section/div/div[1]/div/h3
商标申请进度状态：//div[@class="text"]
商标信息(需要用取到的循环遍历.text属性)：//div[@class="sub-part"]/table/tr/td
商标流程1： //div[@class="e_history"]/div/div/div/div[1]
商标流程2： //div[@class="e_history"]/div/div/div/div[2]
申请人(需要点击进入获取联系方式)：/html/body/div[1]/div[2]/div[2]/div[1]/section/div/div[2]/div[4]/table/tr[1]/td[2]/span/a
电话和邮箱联系方式：//div[@class="rline"]/span[1]/span
下一页就不弄了，需要VIP

可以根据奇偶来存入csv表格
申请进度标题 商标申请进度 申请进度状态 ['商标申请', '1987-06-23', '初审公告', '1988-01-10', '已注册', '1988-04-10', '终止']
商标基本信息 ['商标图案', '', '商标名称', '阿里', '国际分类', '29类 食品', '申请/注册号', '311683', '商标状态', '商标无效', '是否共有商标', '否', '商标类型', '普通商标', '优先权日期', '-', '商标形式', '-', '国标注册日期', '-', '后期指定日期', '-', '类似群', '', '商标申请日期', '1987-06-23', '专用权期限', '-', '初审公告期号', '202', '初审公告日期', '1988-01-10', '注册公告期号', '211', '注册公告日期', '1988-04-10', '申请人名称(中文)', '江苏阿里山（集团）公司', '申请人名称(英文)', '-', '申请人地址(中文)', '江苏常熟市阳桥', '申请人地址(英文)', '-', '代理/办理机构', '-']
商标流程状态时间 ['6\n2009-06-27', '5\n1999-01-28', '4\n1998-04-21', '3\n1988-04-10', '2\n1988-01-10', '1\n1987-06-23'] 商标流程状态申请返回内容 ['无效公告', '无效公告', '续展公告', '商标注册申请-注册公告-结束', '商标注册申请-初审公告-结束', '商标注册申请-申请收文-结束']
联系方式 ['-', '暂无', '暂无']
"""
