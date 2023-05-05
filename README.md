# yan_motor
在学习《Electric Motors and Drives: Fundamentals, Types and Applications. 3rd Edition》时，对于电机和控制电路的一些特性，通过建立微分方程组来进行仿真探究。  

- [x] [直流电机特性](./dc_motor.ipynb)  
- [x] [直流电机的PID 控制](./dc_motor_pid.ipynb)  
- [x] 重构，使得控制系统的结构更加清晰，而不是所有的代码都挤在同一的模块中  
  - [x] 添加系统信息，模块作为系统的一部分  
  - [x] ~~给模块添加输入输出变量~~：通过输入输出变量并不能使得代码更加直观，可能还会存在引用未定义变量的风险，故不做处理  
  - [x] 通过有序字典存储模块和状态变量   


## 使用说明   
因为系统、模块与状态变量之间存在着相互依赖，尤其是构造函数部分，所以最好只是用以下推荐的函数。一个[简单的使用示例](./examples/test_new_system.ipynb)

- `System`  
  - `sys = System(name="sys", h=0.001, execution_time=10)`: 创建系统  
  - `mod = sys.createModule(name)`: 创建模块  
  - `sys.run(execution_time)`: 运行一段时间，默认为系统的执行时间    
  - `sys.reset()`: 重置系统数据，但保留系统的各个模块与状态结构    
  - `sys.draw(['modName_stateName'])`: 绘制系统中的变量随时间变化的曲线      
- `Module`
  - `theta = motor.createState(name="theta", func=lambda: omega, init_value=0)`: 创建变量    
- `State`：使用说明如下
  - `State` 方程的计算结果应该是该变量的微分，方程中的变量如果不是特殊说明`.prime()` 引用到的确实状态变量的值
  - `theta.prime()`: 用户获取状态方程的微分部分，有时候会用到，尤其是在算术方程转微分方程时  
- `AEQ`：普通算术方程
  - 方程中引用的变量是其他变量的值，计算结果是该算术变量的值

以`x'=x, x_0 = 1` 为例，可以按以下形式构造状态变量：  
```python  
# x' = x, x初始值为1
x = mod.createState(name="x", func=lambda: x, init_value=1)
```