"""
SVM 鸢尾花分类实验 —— 原始文件读取版本
=========================================
任务描述:
  构建一个 SVM 模型，根据鸢尾花的花萼和花瓣大小将其分为三种不同的品种。
  - 特征: 花萼长度(sepal length), 花萼宽度(sepal width), 花瓣长度(petal length), 花瓣宽度(petal width)
  - 标签: 0=山鸢尾(Iris-setosa), 1=变色鸢尾(Iris-versicolor), 2=维吉尼亚鸢尾(Iris-virginica)

数据集:
  从本地文件 iris.data 读取，文件路径与题目.md 在同一目录下。
  数据共150行, 每行4个特征 + 1个标签。

实验步骤:
  Step 1: 数据准备 —— 加载数据、分割训练集/测试集
  Step 2: 模型搭建 —— 构建 SVM 分类器 (线性核, OVR)
  Step 3: 模型训练 —— 使用训练集拟合模型
  Step 4: 模型评估 —— 计算准确率、可视化决策边界
"""

import numpy as np
import os
from matplotlib import colors
from sklearn import svm
from sklearn.svm import SVC
from sklearn import model_selection
import matplotlib
matplotlib.use('Agg')           # 使用非交互式后端, 避免 plt.show() 阻塞
import matplotlib.pyplot as plt
import matplotlib as mpl


# ============================================================================
# 数据文件路径: 与题目.md 在同一目录下
# ============================================================================
# 获取当前脚本所在目录，拼接数据文件名
#_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#data_path = os.path.join(_SCRIPT_DIR, 'iris.data')
# 原始实验环境路径 (保留以作参考):
data_path = '/home/aistudio/data/data5420/iris.data'


# ============================================================================
# Part 1: 辅助函数定义
# ============================================================================

def iris_type(s):
    """
    将鸢尾花标签转换为整数类别。
    从文件读取时 np.loadtxt 传入的是字节串 (bytes)。
    例如: b'Iris-setosa' -> 0
    """
    it = {b'Iris-setosa': 0, b'Iris-versicolor': 1, b'Iris-virginica': 2}
    return it[s]


def classifier():
    """
    构建 SVM 分类器。

    参数说明:
      C:     误差项惩罚系数, 默认值为1。
             C 越大, 对误分类的惩罚越大, 趋向于对训练集全分对,
             训练集准确率很高但泛化能力弱 (过拟合)。
             C 越小, 对误分类的惩罚越小, 允许容错, 泛化能力较强。
      kernel: 'linear' 为线性核; 'rbf' 为高斯核。
      decision_function_shape:
             'ovr' (one vs rest): 一个类别与其他类别进行划分。
             'ovo' (one vs one):  类别两两之间进行划分, 用二分类模拟多分类。
    """
    # 另一种可选的配置 (高斯核):
    # clf = svm.SVC(C=0.8, kernel='rbf', gamma=50, decision_function_shape='ovr')
    clf = svm.SVC(C=0.5,
                  kernel='linear',
                  decision_function_shape='ovr')
    return clf


def train(clf, x_train, y_train):
    """
    训练 SVM 模型。
    参数:
      clf:      SVM 分类器
      x_train:  训练集特征向量
      y_train:  训练集目标值 (使用 ravel() 展平)
    """
    clf.fit(x_train, y_train.ravel())


def show_accuracy(a, b, tip):
    """
    比较预测值 a 和真实值 b 是否相等，计算准确率并打印。
    参数:
      a:   预测值
      b:   真实值
      tip: 提示信息 (如 'traing data' / 'testing data')
    """
    acc = a.ravel() == b.ravel()
    print('%s Accuracy:%.3f' % (tip, np.mean(acc)))


def print_accuracy(clf, x_train, y_train, x_test, y_test):
    """
    打印训练集和测试集上的模型评估指标:
      1. score() 直接输出准确率
      2. predict() + show_accuracy() 对比原始结果与预测结果
      3. decision_function() 输出样本到各分割平面的距离
    """
    # 分别打印训练集和测试集的准确率
    # score(x_train, y_train): 返回模型在给定数据上的平均准确率
    print('training prediction:%.3f' % (clf.score(x_train, y_train)))
    print('test data prediction:%.3f' % (clf.score(x_test, y_test)))

    # 原始结果与预测结果进行对比
    # predict(): 对样本进行预测，返回样本类别
    show_accuracy(clf.predict(x_train), y_train, 'traing data')
    show_accuracy(clf.predict(x_test), y_test, 'testing data')

    # 计算决策函数的值，表示各样本到各分割平面(超平面)的距离
    # 对于 OVR 三分类: 每行3个值, 分别代表到类别0/1/2超平面的距离
    print('decision_function:\n', clf.decision_function(x_train))


def draw(clf, x, y, x_test):
    """
    可视化 SVM 分类结果。
    绘制分类背景色块、训练样本点和测试样本点。

    参数:
      clf:    训练好的 SVM 分类器
      x:      全部样本特征 (用于确定绘图范围)
      y:      全部样本标签 (用于着色)
      x_test: 测试集特征 (以空心圆标注)
    """
    iris_feature = ['sepal length', 'sepal width', 'petal length', 'petal width']

    # ---- 1. 生成网格采样点 ----
    x1_min, x1_max = x[:, 0].min(), x[:, 0].max()          # 第0列的范围
    x2_min, x2_max = x[:, 1].min(), x[:, 1].max()          # 第1列的范围
    x1, x2 = np.mgrid[x1_min:x1_max:200j, x2_min:x2_max:200j]  # 生成 200×200 网格
    grid_test = np.stack((x1.flat, x2.flat), axis=1)       # 将网格展平为 (40000, 2) 的测试点矩阵
    print('grid_test:\n', grid_test)

    # ---- 2. 计算网格点到决策面的距离 ----
    z = clf.decision_function(grid_test)
    print('the distance to decision plane:\n', z)

    # ---- 3. 预测网格点的分类 ----
    grid_hat = clf.predict(grid_test)                      # 预测分类值, 得到 [0, 0, ..., 2, 2, 2]
    print('grid_hat:\n', grid_hat)
    grid_hat = grid_hat.reshape(x1.shape)                  # 重塑为与 x1 一致的形状 (200, 200)

    # ---- 4. 绘图 ----
    cm_light = mpl.colors.ListedColormap(['#A0FFA0', '#FFA0A0', '#A0A0FF'])
    cm_dark = mpl.colors.ListedColormap(['g', 'b', 'r'])

    plt.pcolormesh(x1, x2, grid_hat, cmap=cm_light)                                  # 背景色块: 分类区域
    plt.scatter(x[:, 0], x[:, 1], c=np.squeeze(y), edgecolor='k', s=50, cmap=cm_dark) # 全部样本点 (实心)
    plt.scatter(x_test[:, 0], x_test[:, 1], s=120, facecolor='none', zorder=10)       # 测试样本点 (空心圆)
    plt.xlabel(iris_feature[0], fontsize=20)
    plt.ylabel(iris_feature[1], fontsize=20)
    plt.xlim(x1_min, x1_max)
    plt.ylim(x2_min, x2_max)
    plt.title('SVM in iris data classification', fontsize=30)
    plt.grid()
    plt.savefig('svm_iris_classification_result.png', dpi=150, bbox_inches='tight')
    print('分类结果图已保存为: svm_iris_classification_result.png')
    plt.close()


# ============================================================================
# Part 2: 主程序
# ============================================================================

def main():
    """
    主函数: 按实验步骤依次执行:
      1) 加载数据（从本地 iris.data 文件读取）
      2) 数据分割
      3) 构建模型
      4) 训练模型
      5) 评估模型
      6) 可视化
    """
    # ---------- Step 1: 数据准备 ----------
    # 从本地文件读取数据
    data = np.loadtxt(data_path,              # 数据文件路径
                      dtype=float,            # 数据类型
                      delimiter=',',          # 数据分隔符
                      converters={4: iris_type})  # 将第5列使用 iris_type 转换

    # data 为二维数组, shape=(150, 5)
    # print(data)
    print(f"数据形状: {data.shape}")

    # 数据分割 —— 按列切分: 前4列为特征 x, 第5列为标签 y
    x, y = np.split(data, (4,), axis=1)

    # 取前两列特征用于可视化 (花萼长度、花萼宽度)
    # 若要使用全部4列特征，改为: x = x[:, 0:4]
    x = x[:, 0:2]
    # print(x)

    # 划分训练集和测试集
    x_train, x_test, y_train, y_test = model_selection.train_test_split(
        x,                  # 样本特征集
        y,                  # 样本标签
        random_state=1,     # 随机数种子 (保证结果可复现)
        test_size=0.3       # 测试样本占比 30%
    )

    # ---------- Step 2: 模型搭建 ----------
    clf = classifier()

    # ---------- Step 3: 模型训练 ----------
    train(clf, x_train, y_train)

    # ---------- Step 4: 模型评估 ----------
    print_accuracy(clf, x_train, y_train, x_test, y_test)

    # ---------- Step 5: 可视化 ----------
    draw(clf, x, y, x_test)


# ============================================================================
# 程序入口
# ============================================================================
if __name__ == '__main__':
    main()
