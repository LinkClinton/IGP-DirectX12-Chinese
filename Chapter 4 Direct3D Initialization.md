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

### <span id = "4.1.3"> 4.1.3 Textures Formats </span>

一个二维纹理是一个数据矩阵。
如果我们使用二维纹理去存储图片的话，那么每个元素里面存储的就是每个像素的颜色。
当然这并不是二维纹理的唯一用处。
`Normal mapping`技术中，每个元素储存的就是一个三维向量，而不是颜色。
虽然纹理通常被用来储存图片数据，但是还是有很多其他用途的。
一个一维纹理就是一个一维数组，二维纹理就是一个二维数组，三维纹理就是一个三维数组。
但是纹理并不单纯只是数组，这个我们会在稍后的章节中讨论到。
纹理有`mipmap levels`，`GPU`可以在这上面做一些特殊的操作，例如过滤和多重采样。
但是纹理并不能存储任意类型的数据，他只能存储一些具体的数据类型，参见`DXGI_FORMAT`。

- `DXGI_FORMAT_R32G32B32_FLOAT`: 每个元素由3个`32bit`大小的浮点型组成。
- `DXGI_FORMAT_R16G16B16A16_UNORM`: 每个元素由4个`16bit`大小的无符号类型组成。
- `DXGI_FORMAT_R32G32_UINT`: 每个元素由2个`32bit`大小的无符号整型组成。
- `DXGI_FORMAT_R8G8B8A8_UNORM`: 每个元素由4个`8bit`大小的无符号类型组成。
- `DXGI_FORMAT_R8G8B8A8_SNORM`: 每个元素由4个`8bit`大小的有符号类型组成。
- `DXGI_FORMAT_R8G8B8A8_SINT`: 每个元素由4个`8bit`大小的有符号整型组成。
- `DXGI_FORMAT_R8G8B8A8_UINT`: 每个元素由4个`8bit`大小的无符号整型组成。

枚举中的`R`,`G`,`B`,`A`通常表示红色，绿色，蓝色和`Alpha`。
颜色是由前面三种颜色组合而成的。而`Alpha`值通常是用于控制物体的透明度的。
纹理中实际存储的元素的类型并不一定要和这个纹理定义的类型一样。
例如`DXGI_FORMAT_R32G32B32_FLOAT`,由3个浮点型组成，那么我同样可以在纹理中存储一个三维向量。
虽然由定义一个纹理的类型，但是并没有强制要求类型，我们只是在一个纹理被绑定到管道上去的时候，将纹理数据放到预留的内存空间里面去。

### <span id = "4.1.4"> The Swap Chain and Page Flipping </span>

为了避免绘制的时候闪烁，最好的方法就是将要绘制的这一帧绘制到一个离屏的纹理(`Back Buffer`)中去。
只要我们将要绘制的内容全部绘制到`Back Buffer`中去，我们就可以将这一帧呈现到屏幕中去。
这样的话，观看者就不会看到绘制的过程，而是看到完整的一帧。
为了实现这样的技术，我们需要维持两个纹理，一个叫做`Front Buffer`，一个叫做`Back Buffer`。
`Front Buffer`存储正在显示的图片数据，然后下一帧正在绘制到`Back Buffer`中去。
当下一帧绘制完成的时候，我们就切换这两个纹理，`Front Buffer`变成了`Back Buffer`,`Back Buffer`变成了`Front Buffer`。
将这两个纹理切换的过程我们就称之为呈现`presenting`。呈现是一个效率非常高的操作，他只是将两个纹理的指针交换了而已。可以参见图片[4.1](#Image4.1)。

<img src="Images/4.1.png" id = "Image4.1"> </img>

我们通常使用交换链来管理这两个纹理。在`Direct3D`中，我们使用`IDXGISwapChain`来管理。
交换链中存储着着两个纹理。我们可以使用`ResizeBuffers`来改变着两个纹理的大小。`Present`来呈现。

使用两个纹理作为`Buffer`的技术我们称作双缓冲。当然你可以使用更多的`Buffer`。


