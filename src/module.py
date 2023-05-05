
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .system import System

from .state import State
from .aeq import AEQ
from collections import OrderedDict


class Module(object):
    def __init__(self, name, sys: 'System') -> None:
        """
        创建一个模块，并且内置一个_time 变量  
        Args:  
            name (str): 模块名  
            sys (System): 上层系统 
        """
        self.name = name
        self.sys = sys
        self.states: OrderedDict[str, 'State'] = OrderedDict()

    def get_h(self):
        return self.sys.get_h()

    def get_index(self):
        return self.sys.get_index()

    def createState(self,
                    name="state",
                    func: Callable[['Module'], float] = lambda mod: .0,
                    init_value=0):
        """        
        从模块中创建一个状态变量  

        Args:              
            init_value (float): 该状态变量的初始值，默认为0   
            func (Callable[[], float]): 一个函数对象用于计算该状态变量的微分 

        Returns:  
            state (State): 对于该状态变量的引用
        """
        state_name = name
        if self.states.get(state_name):
            print("【警告】状态名已存在，以前的状态变量将被覆盖掉")
        state = State(state_name, self, init_value, func)
        self.states[state_name] = state
        return state

    def createAEQ(self,
                  name="aeq",
                  func: Callable[['Module'], float] = lambda mod: .0):
        """        
        从模块中创建一个算术方程变量  

        Returns:  
            state (State): 对于该变量的引用
        """
        state_name = name
        if self.states.get(state_name):
            print("【警告】状态名已存在，以前的状态变量将被覆盖掉")
        state = AEQ(state_name, self, func)
        self.states[state_name] = state
        return state

    def calc_kn(self):
        """
        计算k1~k4 数据
        """
        for k, s in self.states.items():
            s.calc_kn()

    def calc_k0(self):
        """
        根据上面计算的k1~k4 数据，计算这一步的k0 和结果
        """
        for k, s in self.states.items():
            s.calc_k0()

    def reset(self):
        """
        重置模块，主要是重启模块中的状态变量   
        """
        self.index = 0
        for k, s in self.states.items():
            s.reset()

    def getStateNames(self):
        """
        获取模块的所有变量名，格式为字符串的数组，其中的元素命名方式为：模块名_变量名
        """
        res = []
        for k, s in self.states.items():
            res.append("%s_%s" % (self.name, k))
        return res

    def getStateValues(self):
        """
        获取模块的所有变量值，返回一个数值型的数组
        """
        res = []
        for k, s in self.states.items():
            res.append(s.curr_value)
        return res
