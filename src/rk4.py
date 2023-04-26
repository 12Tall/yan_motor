from typing import Callable


class Module():
    def __init__(self, name="module", h=0.001, end=5) -> None:
        """
        创建一个模块，并且内置一个_time 变量  
        Args:  
            name (str): 模块名  
            h (float): 步长，默认0.001s  
            end (float): 终止时间，默认5s
        """
        self.name = name
        self.h = h
        self.index = 0
        self.end = end
        self._time = State("_time", self, 0, lambda: 1)

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
        state_name = self.name + "_" + name
        # if getattr(self, state_name):
        #     print("【警告】状态名已存在，以前的状态变量将被覆盖掉")
        state = State(state_name, self, init_value, func)
        setattr(self, state_name, state)
        return state

    def reset(self):
        """
        重置模块，主要是重启模块中的其他状态变量   
        """
        self.index = 0
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if(isinstance(prop, State)):
                prop.reset()

    def calc_k1_to_k4(self):
        """
        计算k1~k4 数据
        """
        for prop_name in dir(self):
            # 遍历所有属性，筛选State 类型用于计算，似乎是按属性名排序的
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                val = prop.func()  # 重载运算符导致需要在计算k 值使需要额外的处理
                prop.k[self.get_index()] = val.val(
                ) if isinstance(val, State) else val

    def calc_k0(self):
        """
        根据上面计算的k1~k4 数据，计算这一步的k0 和结果
        """
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                prop.calc()

    def calc(self):
        for index in range(1, 5):  # 计算每个属性的 k1,k2,k3,k4
            self.index = index
            self.calc_k1_to_k4()
        self.calc_k0()

    def getStateName(self):
        res = []
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                res.append(prop_name)
        return res

    def getStateValue(self):
        res = []
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                res.append(prop.curr_value)
        return res

    def run(self):
        res = []
        res.append(self.getStateName())
        for i in range(0, int(self.end/self.h)):
            self.calc()
            res.append(self.getStateValue())
        return res


class State():
    """
    状态变量，但是不要直接创建该类型的实例，而是需要通过Module.createState() 来创建，因为有些内部的参数需要从Module 中获取。   
    正常运算如果需要用到该状态的值的话，可以通过`state.val()` 方法获取。简单的加减乘除运算已经通过重载运算符可以直接使用`state` 变量运算。  
    """

    def __init__(self,
                 name,
                 mod: Module,
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
    
    def calc(self):
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

    def __truediv__ (self, other):
        return self.__div(other)

    def __rtruediv__ (self, other):
        return self.__div(other)

    def __div(self, other):
        if isinstance(other, State):
            return self.val() / other.val()
        else:
            return self.val() / other

    def __neg__(self):
        return -self.val()