
from collections import OrderedDict
from typing import List
from .module import Module


class System(object):

    def __init__(self, name="sys", h=0.001, execution_time=10) -> None:
        self.name = name
        self.h = h
        self.execution_time = execution_time
        self.result = []
        self.modules: OrderedDict[str, 'Module'] = OrderedDict()
        self.index = 0
        self.timer = self.createModule("timer").createState('time', lambda: 1, init_value=0)

    def get_h(self):
        """
        获取步长
        """
        return self.h

    def get_index(self):
        """
        当前正在计算k{?}
        """
        return self.index

    def createModule(self, name="mod"):
        """        
        从系统中创建一个模块  

        Args:              
            name (str): 模块名 
        Returns:  
            module (Module): 对于该模块的引用
        """
        module_name = name
        if self.modules.get(module_name) != None:
            print("【警告】模块已存在，以前的模块将被覆盖掉")
        module = Module(name, self)
        self.modules[module_name] = module
        return module

    def calc_kn(self):
        """
        计算k1~k4 数据
        """
        for key, mod in self.modules.items():
            mod.calc_kn()

    def calc_k0(self):
        """
        根据上面计算的k1~k4 数据，计算这一步的k0 和结果
        """
        for key, mod in self.modules.items():
            mod.calc_k0()

    def calc(self):
        """
        计算k1~k4
        """
        for index in range(1, 5):  # 计算每个属性的 k1,k2,k3,k4
            self.index = index
            self.calc_kn()
        self.calc_k0()

    def reset(self):
        """
        重置整个系统
        """
        self.index = 0
        self.result.clear()
        for key, mod in self.modules.items():
            mod.reset()

    def getStateNames(self):
        """
        获取模块的所有模块变量名，格式为字符串的数组，其中的元素命名方式为：模块名_变量名
        """
        res = []
        for key, mod in self.modules.items():
            res.extend(mod.getStateNames())
        return res

    def getStateValues(self):
        """
        获取模块的所有变量值，返回一个数值型的数组
        """
        res = []
        for key, mod in self.modules.items():
            res.extend(mod.getStateValues())
        return res

    def run(self, execution_time=0):
        """
        运行仿真，如果没有给定时间的话，则以系统默认时间为准
        """
        t = execution_time if execution_time > 0 else self.execution_time
        for i in range(0, int(t/self.h)):
            self.calc()
            self.result.append(self.getStateValues())
        return self.result

    def draw(self, labels: List[str]):
        """
        绘制系统的时域响应，需要指定标签如：['moduleName_stateName', ...]
        """
        import pandas as pd
        import matplotlib.pyplot as plt

        data = pd.DataFrame(self.result, columns=self.getStateNames())
        for label in labels:
            plt.plot(data["timer_time"], data[label], label=label)

        plt.legend()
        plt.show()
