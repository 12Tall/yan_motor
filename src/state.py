

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .module import Module


class State(object):
    """
    状态变量，但是不要直接创建该类型的实例，而是需要通过Module.createState() 来创建，因为有些内部的参数需要从Module 中获取。   
    正常运算如果需要用到该状态的值的话，可以通过`state.val()` 方法获取。简单的加减乘除运算已经通过重载运算符可以直接使用`state` 变量运算。  
    """

    def __init__(self,
                 name,
                 mod: 'Module',
                 init_value,
                 func: Callable[[], float]):
        """
        初始化一个状态变量  

        Args:  
            name (str): 变量名
            init_value (float): 该状态变量的初始值
            mod (Module): 状态变量所在的模块  
            func (Callable[[], float]): 一个函数对象用于计算该状态变量的微分     
        """
        self.name = name
        self.init_value = init_value
        self.curr_value = init_value
        self.mod = mod
        self.func = func
        self.k = [.0, .0, .0, .0, .0]
        # 用于计算状态变量的临时值，假设当前是在计算k3，那么temp_value = curr_value + 0.5 * h *k2
        self.val_coeff = [0, 0, 0.5, 0.5, 1]  # 第一个元素不会用到，只是用来占位的

    def val(self):
        """
        根据k_n 计算状态值，并将该状态值作为求解k_{n+1} 的参数返回给lambda 函数
        """
        index = self.mod.get_index()
        return self.curr_value + self.val_coeff[index]*self.mod.get_h() * self.k[index-1]

    def prime(self):
        """
        状态变量的微分值
        """
        return self.func()

    def calc_kn(self):
        """
        计算k1~k4 数据
        """
        val = self.func()  # 重载运算符导致需要在计算k 值使需要额外的处理
        self.k[self.mod.get_index()] = val.val() if isinstance(val, State) else val

    def calc_k0(self):
        """
        计算最终斜率存储到k0，并利用k0 算出最终结果    
        k = (k1 + 2*k2 + 2*k3 + k4)/6
        """
        self.k[0] = (self.k[1]+2*self.k[2]+2*self.k[3]+self.k[4])/6
        self.curr_value = self.curr_value + self.mod.get_h()*self.k[0]

    def reset(self):
        """
        重置状态变量
        """
        self.curr_value = self.init_value

    ########## 以下是重载运算符的部分 ##########
    def __mul__(self, other):
        return self.__mul(other)

    def __rmul__(self, other):
        return self.__mul(other)

    def __mul(self, other):
        if isinstance(other, State):
            return self.val() * other.val()
        else:
            return self.val() * other

    def __add__(self, other):
        return self.__add(other)

    def __radd__(self, other):
        return self.__add(other)

    def __add(self, other):
        if isinstance(other, State):
            return other.val() + self.val()
        else:
            return self.val() + other

    def __sub__(self, other):
        return self.__sub(other)

    def __rsub__(self, other):
        return self.__sub(other)

    def __sub(self, other):
        if isinstance(other, State):
            return self.val() - other.val()
        else:
            return self.val() - other

    def __truediv__(self, other):
        return self.__div(other)

    def __rtruediv__(self, other):
        return self.__div(other)

    def __div(self, other):
        if isinstance(other, State):
            return self.val() / other.val()
        else:
            return self.val() / other

    def __neg__(self):
        return -self.val()
