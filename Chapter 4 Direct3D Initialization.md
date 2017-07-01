# <span id = "4"> Chapter 4 Direct3D Initialization </span>

初始化`Direct3D`我们需要了解一些基础的`Direct3D`类型和一些基础的图形概念。
我们将在这一章的第一段和第二段讲述这些知识。
然后我们就介绍初始化`Direct3D`必要的步骤。
之后稍微绕一点远路，介绍下精确的计时和用于实时图形应用的时间测量方法。

**目标**

- 基本上了解`Direct3D`在3D程序编写上扮演的角色。
- 理解`COM`在`Direct3D`里面中的作用。
- 了解基本的图形概念，例如2D图片如何储存的，页面的过滤，深度缓存，多重采样和`CPU`与`GPU`的交互。
- 学习如何使用计时函数实现高精度的计时器。
- 学习如何初始化`Direct3D`。

## <span id = "4.1"> 4.1 PRELIMINARIES </span>

初始化`Direct3D`我们需要了解一些基础的`Direct3D`类型和一些基础的图形概念。
我们在这一段中介绍这些类型和概念，所以不要认为我们离题了。

### <span id = "4.1.1"> 4.1.1 Direct3D 12 Overview </span>

`Direct3D` 是一个用于控制和管理`GPU`(**graphics	processing	unit**)的底层的图形`API`(**application	programming	interface**)，它能够让我们使用硬件加速渲染虚拟的3D世界。
我们如果要提交给`GPU`一个指令去清理`Render Target`(屏幕)，我们可以通过使用`Direct3D`函数来做到。
`Direct3D`和硬件驱动将会把`Direct3D`的指令翻译成可以被`CPU`理解的机器语言。
我们并不需要关心具体使用的`GPU`是什么，我们只需要知道他是否支持我们正在使用的`Direct3D`的版本。
通常来说`GPU`厂家，例如`NVIDIA`,`Intel`,`AMD`都会提供支持`Direct3D`的驱动。

`Direct3D 12`增加了一些新的特性，但是相比以前的版本来说，最大的改进还是重新设计了它，减少了对`CPU`的消耗和提高了对多线程的支持。
为了达到这个目的，`Direct3D 12`比`Direct3D 11`变得更加底层，更加接近现代`GPU`架构。
当然使用这样较为麻烦的`API`的优势就是性能得到提升。

### <span id = "4.1.2"> 4.1.2 COM </span>

`Component	Object	Model`(**COM**)是一项能够让`DirectX`与具体的程序语言无关和向后兼容性的技术。
我们通常用接口`Interface`的形式引用一个`COM`组件，使得我们能够将其视为`C++`里面的类，并且当作类使用。
大多数的`COM`细节在我们使用`C++`编写`DirectX`程序的时候就被隐藏了。
唯一需要注意的是我们是通过指定的函数或者另外一个接口去实例化一个`Interface`，而不是通过使用`C++`的关键字`new`。(**Interface通常声明为一个指针**)。
`COM`组件是引用计数的，也就是说当我们不需要使用一个接口的时候，我们就必须通过`Release`方法去释放它(**所有的Interface都是继承自IUnknown的**)。
当一个`COM`组件的引用次数是0的时候我们才会真正的删除这个组件。

为了帮助我们管理`COM`组件的生命周期，`Windows Runtime Library`提供了一个类`Microsoft::WRL::ComPtr`使我们可以将`COM`组件看作一个智能指针。
当一个`ComPtr`实例再也不会被使用的时候，它就会自己调用`Release`释放自己。这样的话我们就不需要关心自己是否需要释放`COM`组件了。

- `Get`: 返回这个`COM`接口的指针。
- `GetAddressOf`:返回这个`COM`接口的指针的地址。
- `Reset`: 将这个实例设置为`nullptr`，同时会自己释放。

当然，还有很多和`COM`组件有关的东西，但是仅仅只是使用`DirectX`的话，那么就没有必要知道那么多细节。

