# Arithmetic Equation
from .state import State

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .module import Module


class AEQ(State):
    """
    普通算术方程，例如：y=x+1
    """

    def __init__(self,
                 name,
                 mod: 'Module',
                 func: Callable[[], float]):
        """
        初始化一个普通算术方程变量  

        Args:  
            name (str): 变量名
            mod (Module): 状态变量所在的模块  
            func (Callable[[], float]): 一个函数对象用于计算该状态变量的微分     
        """
        self.name = name
        self.curr_value = 0
        self.mod = mod
        self.func = func

    def val(self):
        """
        根据k_n 计算返回值
        """
        return self.curr_value

    def prime(self):
        """
        此方法禁止调用
        """
        raise "禁止在算术方程中使用变量的微分"

    def calc_kn(self):
        """
        计算k1~k4 数据，因为是算术方程，所以就直接赋值了
        """
        val = self.func()  # 重载运算符导致需要在计算k 值使需要额外的处理
        self.curr_value = val.val(
        ) if isinstance(val, State) else val

    def calc_k0(self):
        """
        计算最终斜率存储到k0，并利用k0 算出最终结果    
        k = (k1 + 2*k2 + 2*k3 + k4)/6
        """
        val = self.func()  # 重载运算符导致需要在计算k 值使需要额外的处理
        self.curr_value = val.val(
        ) if isinstance(val, State) else val

    def reset(self):
        """
        重置状态变量
        """
        self.curr_value = 0