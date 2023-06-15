import os, datetime
from multiprocessing import Pool

import matplotlib.pyplot as plt
from cnsenti import Sentiment

from wordCloud import saveVariable, loadVariable

def wordAnalysisPerMonth(myArgs):
    """并行处理各月份的数据

    Args:
        month (int): 第几个月份的数据（对应第几个进程）
    """
    month, targetWords = myArgs[0], myArgs[1]
    date = datetime.datetime.strptime(f'2023-{month}-01', '%Y-%m-%d')
    oneDay = datetime.timedelta(days = 1)
    relativeEssayEmotionalAnalysis = []
    senti = Sentiment()

    while date.month == month:
        MonthStrOfThisDate = str(date.month) if date.month >= 10 else '0' + str(date.month)
        dayStrOfThisDate = str(date.day) if date.day >= 10 else '0' + str(date.day)
        thisDateDataDir = './data/2023' + MonthStrOfThisDate + dayStrOfThisDate
        allFilesInThisDate = os.listdir(thisDateDataDir)
        for fileName in allFilesInThisDate:
            filePath = os.path.join(thisDateDataDir, fileName)
            with open(filePath, encoding="utf-8") as f:
                for line in f:
                    for targetWord in targetWords:
                        if targetWord in line:
                            essayEmotion = senti.sentiment_count(line)
                            relativeEssayEmotionalAnalysis.append((essayEmotion['pos'], essayEmotion['neg']))
                            break
        date += oneDay

    return relativeEssayEmotionalAnalysis

def produceWordCount(wordClass):
    targetWords = None
    if wordClass == 'US':
        targetWords =  ['美国', '美方']
    elif wordClass == '14':
        targetWords = ['十四届全国人大', '十四届全国人民代表大会', '两会', '全国政协十四届', '政协第十四届']

    p = Pool(5)
    results = p.map(wordAnalysisPerMonth, [[1,targetWords] , [2, targetWords], [3, targetWords], [4,targetWords], [5,targetWords]])
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('\nAll subprocesses done.\n')

    allWordsRelatedCount = []
    for wordsRelated in results:
        allWordsRelatedCount += wordsRelated
    return allWordsRelatedCount


def drawEmotionalData(emotionalData, emotionalDataClass ):
    positiveData = len([i for i in emotionalData if i[0] > i[1] + 2])
    negativeData = len([i for i in emotionalData if i[1] > i[0] + 2])
    middleData = len(emotionalData) - positiveData - negativeData

    plt.figure(figsize=(7,5)) #调节图形大小
    labels = ['positive','negative','middle'] #定义标签
    drawData = [positiveData, negativeData, middleData] #每块值
    colors = ['#f47920','#444693','#4d4f36'] if emotionalDataClass == '14' \
        else ['#4d4f36', '#7fb80e', '#6950a1']
    title = 'emotional analysis of vocab data about US' if emotionalDataClass == 'US' \
        else 'emotional analysis of vocab data about 14th National People\'s Congress' 
    explode = (0.04, 0.03, 0.02) #将某一块分割出来，值越大分割出的间隙越大
    plt.pie(drawData,
                explode=explode,
                labels=labels,
                colors=colors,
                autopct = '%3.2f%%', #数值保留固定小数位
                shadow = True, #无阴影设置
                startangle =90, #逆时针起始角度设置
                pctdistance = 0.6) #数值距圆心半径倍数的距离
    plt.title(title)
    plt.axis('equal')
    plt.savefig(f'./output/pieChartOfEmotion{emotionalDataClass}.png', dpi = 350)

def emotionalAnalysis():
    try:
        emotionalAnalysisAbout14 = loadVariable('./output/emotionalAlysisAbout14.pickle')
        emotionalAnalysisAboutUS = loadVariable('./output/emotionalAlysisABoutUS.pickle')        
    except:
        emotionalAnalysisAbout14 = produceWordCount('14')
        saveVariable(emotionalAnalysisAbout14, './output/emotionalAlysisAbout14.pickle')

        emotionalAnalysisAboutUS = produceWordCount('US')        
        saveVariable(emotionalAnalysisAboutUS, './output/emotionalAlysisABoutUS.pickle')

    drawEmotionalData(emotionalAnalysisAboutUS, 'US')
    drawEmotionalData(emotionalAnalysisAbout14, '14')






if __name__ == '__main__':
    emotionalAnalysis()