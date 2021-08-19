# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 21:36:55 2019

@author: lenovo
"""
import numpy as np
import xlrd
import pandas as pd

#从excel文件中读取数据
def read(file):
    wb = xlrd.open_workbook(filename=file)#打开文件
    sheet = wb.sheet_by_index(0)#通过索引获取表格
    rows = sheet.nrows # 获取行数
    all_content = []        #存放读取的数据
    for j in range(1, 14):       #取第1~第4列对的数据
        temp = []
        for i in range(1,rows) :
            cell = sheet.cell_value(i, j)   #获取数据 
            temp.append(cell)           
        all_content.append(temp)    #按列添加到结果集中
        temp = []
    return np.array(all_content)

#极小型指标 -> 极大型指标
def dataDirection_1(datas):         
	return np.max(datas)-datas     #套公式

#中间型指标 -> 极大型指标
def dataDirection_2(datas, x_best):
    temp_datas = datas - x_best
    M = np.max(abs(temp_datas))
    answer_datas = 1 - abs(datas - x_best) / M     #套公式
    return answer_datas
    
#区间型指标 -> 极大型指标
def dataDirection_3(datas, x_min, x_max):
    M = max(x_min - np.min(datas), np.max(datas) - x_max)
    answer_list = []
    for i in datas:
        if(i < x_min):
            answer_list.append(1 - (x_min-i) /M)      #套公式
        elif( x_min <= i <= x_max):
            answer_list.append(1)
        else:
            answer_list.append(1 - (i - x_max)/M)
    return np.array(answer_list)   
 
#正向化矩阵标准化
def temp2(datas):
    K = np.power(np.sum(pow(datas,2),axis =1),0.5)
    for i in range(0,K.size):
        for j in range(0,datas[i].size):
            datas[i,j] = datas[i,j] / K[i]      #套用矩阵标准化的公式
    return datas

#计算得分并归一化
def temp3(answer2):
    list_max = np.array([np.max(answer2[0,:]),np.max(answer2[1,:]),np.max(answer2[2,:]),np.max(answer2[3,:]),np.max(answer2[4,:]),np.max(answer2[5,:]),np.max(answer2[6,:]),np.max(answer2[7,:]),np.max(answer2[8,:]),np.max(answer2[9,:]),np.max(answer2[10,:]),np.max(answer2[11,:]),np.max(answer2[12,:])])  #获取每一列的最大值
    list_min = np.array([np.min(answer2[0,:]),np.min(answer2[1,:]),np.min(answer2[2,:]),np.min(answer2[3,:]),np.min(answer2[4,:]),np.min(answer2[5,:]),np.min(answer2[6,:]),np.min(answer2[7,:]),np.min(answer2[8,:]),np.min(answer2[9,:]),np.min(answer2[10,:]),np.min(answer2[11,:]),np.min(answer2[12,:])])  #获取每一列的最小值
    np.savetxt("max_value.dat",list_max)
    np.savetxt("min_value.dat",list_min)
    max_list = []       #存放第i个评价对象与最大值的距离
    min_list = []       #存放第i个评价对象与最小值的距离
    answer_list=[]      #存放评价对象的未归一化得分
    for k in range(0,np.size(answer2,axis = 1)):        #遍历每一列数据
        print(np.size(answer2,axis = 1))
        max_sum = 0
        min_sum = 0
        #rint("k:",k)
        for q in range(0,13):                                #有四个指标
            max_sum += np.power(answer2[q,k]-list_max[q],2)*weights[q]     #按每一列计算Di+
            min_sum += np.power(answer2[q,k]-list_min[q],2)*weights[q]     #按每一列计算Di-
        max_list.append(pow(max_sum,0.5))
        min_list.append(pow(min_sum,0.5))
        np.savetxt("max_list.dat",max_list)
        np.savetxt("min_list.dat",min_list)        
        answer_list.append(min_list[k]/ (min_list[k] + max_list[k]))    #套用计算得分的公式 Si = (Di-) / ((Di+) +(Di-))
        np.savetxt("answertxt.dat",answer_list)
        max_sum = 0
        min_sum = 0
    answer = np.array(answer_list)      #得分归一化
    #归一化
    np.savetxt("normalized.dat",answer / np.sum(answer))
    return (answer / np.sum(answer))


def main():
    file = 'data.xlsx'
    answer1 = read(file)        #读取文件
    #5，6，7极小型对应于4，5，6
    answer2 = []
    for i in range(0, 13):       #按照不同的列，根据不同的指标转换为极大型指标，因为只有四列
        answer = None       
        if(i==4):                     #极小型指标
            answer = dataDirection_1(answer1[4])
            print(i)
        elif(i == 5):
            answer = dataDirection_1(answer1[5])
            print(i)
        elif(i == 6):
            answer = dataDirection_1(answer1[6])
            print(i)
        else:
            answer = answer1[i]      
            print(i)
        answer2.append(answer)
    answer2 = np.array(answer2)         #将list转换为numpy数组
    print(answer2)     #正常
    np.savetxt("zhengxianghua.dat",answer2.T)   
    answer3 = temp2(answer2)            #数组正向化
    print(answer3)
    np.savetxt("biaozhunhua.dat",answer3.T)
    answer4 = temp3(answer3)            #标准化处理去钢
    np.savetxt("score.dat",answer4.T)
    print(answer4)
    data = pd.DataFrame(answer4)        #计算得分
    
    #将得分输出到excel表格中
    writer = pd.ExcelWriter('output.xlsx')		# 写入Excel文件
    data.to_excel(writer, 'page_1', float_format='%.5f')		# ‘page_1’是写入excel的sheet名
    writer.save()
    writer.close()

weights=np.array([0.07,0.07,0.07,0.2,0.1,0.1,0.05,0.05,0.06,0.09,0.03,0.05,0.06])
main()
