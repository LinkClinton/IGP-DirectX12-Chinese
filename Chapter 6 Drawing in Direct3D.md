# <element id = "6"> Chapter 6 DRAWING IN DIRECT3D </element>

在之前的章节中，我们主要是讨论了渲染管道中的一些概念和一些数学知识。
在本章中，我们就转为主要讨论`Direct3D API`，从而来配置渲染管道，编写顶点着色器和像素着色器，以及提交图形到渲染管道并且绘制它。
在本章结束的时候，我们就能够成功绘制一个立方体了。

**目标:**
- 了解一些用于定义，存储绘制图形的`Direct3D API`。
- 了解学习如何编写基础的顶点着色器和像素着色器代码。
- 了解如何使用管道状态来配置渲染管道。
- 了解如何创建一个常缓冲并且将其绑定到渲染管道中去，并且熟悉`Root Signature`(暂且叫做根特征，主要是用于定义在着色器使用哪些资源)。

## <element id = "6.1"> 6.1 VERTICES AND INPUT LAYOUTS </element>

回顾5.5.1，在`Direct3D`中，顶点除了他的位置外它还可以附加一些其他数据。
为了创建一个自定义的顶点格式，我们需要创建一个结构体来描述我们要给顶点附加的数据。
下面就举出两个不同的顶点格式的例子，其中一个附加了位置和颜色数据，另外一个附加了位置，法向量，以及两个纹理坐标数据。

```C++

struct Vertex1
{
    Float3 Pos;
    Float4 Color;
};

struct Vertex2
{
    Float3 Pos;
    Float3 Normal;
    Float2 Tex0;
    Float2 Tex1;
};

```

