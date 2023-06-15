import os, datetime
from collections import Counter
from multiprocessing import Pool
import jieba
import numpy as np
import matplotlib.pyplot as plt

from wordCloud import saveVariable, loadVariable

TARGETWORDS = ['十四届全国人大', '十四届全国人民代表大会', '两会', '全国政协十四届',
                '政协第十四届']

def wordAnalysisPerMonth(month):
    """并行处理各月份的数据

    Args:
        month (int): 第几个月份的数据（对应第几个进程）
    """
    date = datetime.datetime.strptime(f'2023-{month}-01', '%Y-%m-%d')
    oneDay = datetime.timedelta(days = 1)
    allWordsCountAboutTargetInThisMonth = Counter()

    while date.month == month:
        MonthStrOfThisDate = str(date.month) if date.month >= 10 else '0' + str(date.month)
        dayStrOfThisDate = str(date.day) if date.day >= 10 else '0' + str(date.day)
        thisDateDataDir = './data/2023' + MonthStrOfThisDate + dayStrOfThisDate
        allFilesInThisDate = os.listdir(thisDateDataDir)
        for fileName in allFilesInThisDate:
            filePath = os.path.join(thisDateDataDir, fileName)
            with open(filePath, encoding="utf-8") as f:
                context = f.readlines()
                context = "".join(context)
                for targetWord in TARGETWORDS:
                    if targetWord in context:
                        allWordsCountAboutTargetInThisMonth += Counter(jieba.lcut(context))
                        break
        date += oneDay

    return allWordsCountAboutTargetInThisMonth

def produceWordCount():
    p = Pool(5)
    results = p.map(wordAnalysisPerMonth, [1, 2, 3, 4, 5])
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('\nAll subprocesses done.\n')

    allWordsRelatedCount = Counter()
    for wordsRelated in results:
        allWordsRelatedCount += wordsRelated

    return allWordsRelatedCount

def wordsInVocabDistribution(allWordsRelatedCount):
    
    allWordsRelatedCount = np.log(allWordsRelatedCount)
    plt.plot(allWordsRelatedCount)
    plt.xlabel('WordIndex')
    plt.ylabel('log of words count')
    plt.title('words distribution in the vocab')
    plt.savefig('./output/wordsInVocabDistribution.png', dpi = 600)

def wordsFrequencyDistribution(allWordsRelatedCount):
    wordsFrequencyData = []
    xLabel = []

    wordsFrequencyData.append(np.sum(allWordsRelatedCount == 1))
    xLabel.append('1')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount == 2))
    xLabel.append('2')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount == 3))
    xLabel.append('3')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount == 4))
    xLabel.append('4')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount == 5))
    xLabel.append('5')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount > 5) - np.sum(allWordsRelatedCount > 10))
    xLabel.append('6~10')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount > 10) - np.sum(allWordsRelatedCount > 50))
    xLabel.append('11~50')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount > 50) - np.sum(allWordsRelatedCount > 100))
    xLabel.append('51~100')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount > 100) - np.sum(allWordsRelatedCount > 1000))
    xLabel.append('101~1000')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount > 1000) - np.sum(allWordsRelatedCount > 10000))
    xLabel.append('1001~10000')

    wordsFrequencyData.append(np.sum(allWordsRelatedCount > 10000))
    xLabel.append('>10000')

    fig, ax = plt.subplots(figsize=(13,4), dpi=600)
    bar = plt.bar(xLabel, wordsFrequencyData, 0.5, color='coral',edgecolor='grey')
    ax.set_title('words frequency distribution')
    ax.set_xlabel('frequency')
    ax.set_ylabel('number')

    # 显示数据标签
    for a,b in zip(xLabel, wordsFrequencyData):
        plt.text(a,b,
                b,
                ha='center', 
                va='bottom',
                )
        
    fig.savefig('./output/wordsFrequencyDistribution.png', dpi = 600)


def createTwoWordDistribution():
    try:
        allWordsRelatedCount = loadVariable( './output/allWordsRelated.pickle')
    except:
        allWordsRelated = produceWordCount()
        saveVariable(allWordsRelated, './output/allWordsRelated.pickle')

    allWordsRelatedCount = list(allWordsRelatedCount.items())
    allWordsRelatedCount = [i[1] for i in allWordsRelatedCount]
    allWordsRelatedCount.sort(reverse=True)
    allWordsRelatedCount = np.array(allWordsRelatedCount)
    wordsInVocabDistribution(allWordsRelatedCount)
    wordsFrequencyDistribution(allWordsRelatedCount)

if __name__=='__main__':
    createTwoWordDistribution()