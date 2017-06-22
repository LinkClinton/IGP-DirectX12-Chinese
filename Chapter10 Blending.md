# Chapter10 Blending

观察下方图片[10.1](Images/10.1.png)。
我们在这一帧中最开始渲染的是地形和木箱，因此地形和木箱的像素就被储存在后台缓冲中。
然后我们使用混合技术来绘制一个水面到后台缓冲，因此水的像素和地形以及木箱的像素在后台缓冲中得到了混合，看起来就是木箱和地形穿过了水面。
在本章中，我们尝试混合技术，这个技术能够就是混合(组合)现在正在光栅化的像素(我们称之为源)和之前已经完成光栅化并存储在后台缓冲中的像素(我们称之为目标)。
这个技术能够让我们去渲染透明的物体，例如水和玻璃。

![10.1](Images/10.1.png)


**目标**

- 理解如何使用混合，并且能够在`Direct3D`中使用它。
- 学习`Direct3D`支持的不同的混合模式。
- 发现如何通过使用Alpha去控制图元的透明度。
- 学习如何使用HLSL中的Clip函数阻止一个像素绘制到后台缓冲中。

## 10.1 THE BLENDING EQUATION

我们设C<sub>src</sub>表示从我们的像素着色器(PixelShader)输出的第i,j个像素，也就是我们正在光栅化的像素，然后我们设C<sub>dst</sub>表示现在在后台缓冲中第i,j个像素。
如果不使用混合技术的话，像素C<sub>src</sub>将会替代C<sub>dst</sub>(前提是他能够通过深度和模板测试)。
但是在使用混合的情况下，C<sub>src</sub>和C<sub>dst</sub>将会混合成一个新的颜色C，并且C将会替代C<sub>dst</sub>作为后台缓冲里面的像素(你可以认为新的颜色C将会被写入到后台缓冲中去)。
`Direct3D`使用下面的这个方程来混合源和目标像素的颜色:

**<center>C = C<sub>src</sub> × F<sub>src</sub> ^ C<sub>dst</sub> × F<sub>dst</sub></center>**

F将会在下面介绍，主要是通过F来让我们有更多的方式去实现更多的效果。
`×` 符合表示的是向量的点积，`^`(他那个符合我打不出，我们暂且叫做混合操作)符号是一种由我们自主定义的运算，具体下面会介绍。

上面的方程是用于处理颜色分量中的RGB的，对于Alpha值我们单独使用下面的方程处理，这个方程和上面的是极为相似的：

**<center>A = A<sub>src</sub>F<sub>src</sub> ^ A<sub>dst</sub>F<sub>dst</sub></center>**

这个方程基本上是一样的，但是这样分开处理的话就可以让`^`运算可以不同了。我们将RGB和Alpha分开处理的动机就是让我们能够单独处理RGB和Alpha值，而两者不互相影响。


## 10.2 BLEND OPERATIONTS

- `D3D12_BLEND_OP_ADD`: **C = C<sub>src</sub> × F<sub>src</sub> + C<sub>dst</sub> × F<sub>dst</sub>**
- `D3D12_BLEND_OP_SUBTRACT`: **C = C<sub>dst</sub> × F<sub>dst</sub> - C<sub>src</sub> × F<sub>src</sub>**
- `D3D12_BLEND_OP_REV_SUBTRACT`: **C = C<sub>src</sub> × F<sub>src</sub> - C<sub>dst</sub> × F<sub>dst</sub>** 
- `D3D12_BLEND_OP_MIN`: **C = min(C<sub>src</sub>, C<sub>dst</sub>)**
- `D3D12_BLEND_OP_MAX`: **C = max(C<sub>src</sub>, C<sub>dst</sub>)**

Alpha的混合操作也是一样的。
当然你可以使用不同的操作来分别处理RGB和Alpha的混合。
举个例子来说，你可以在RGB的混合中使用`+`，然后在Alpha的混合中使用`-`。

**<center>C = C<sub>src</sub> × F<sub>src</sub> + C<sub>dst</sub> × F<sub>dst</sub></center>** 

**<center>A = A<sub>dst</sub>F<sub>dst</sub> - A<sub>src</sub>F<sub>src</sub></center>**


最近在`Direct3D`中加入了一个新的特征(`D3D12_LOGIC_OP`)，我们可以使用逻辑运算符来代替上面的混合操作。
具体的我就没必要放进去了，毕竟很简单理解。

但是你需要注意的是，如果你使用逻辑运算符代替混合操作，你需要注意的是逻辑运算符和传统运算符是不能同时使用的，你必须在这两种里面选择一种使用。
并且你使用逻辑运算符的话，你需要确保你的`Render Target`的格式支持(支持的格式应当是`UINT`的变种)。
## 10.3 BLEND FACTORS

通过改变`Factors(因素)`，我们可以设置更多的不同的混合组合，从而来实现更多的不同的效果。
我们将会在下面解释一些混合组合，但是你还是要去体验一下他们的效果，从而能够有一个概念。
下面将会介绍一些基础的`Factors`。你可以去看SDK文档里面的`D3D12_BLEND`枚举了解到更多高级的`Factors`。
我们设**C<sub>src</sub> = (r<sub>src</sub>, g<sub>src</sub>, b<sub>src</sub>)**，**A<sub>src</sub> = a<sub>src</sub>**(这个RGBA值是由像素着色器输出的)，
**C<sub>dst</sub> = (r<sub>dst</sub>, g<sub>dst</sub>, b<sub>dst</sub>)**，**A<sub>dst</sub> = a<sub>dst</sub>**(这个RGBA值是存储在后台缓冲中的)。

- `D3D12_BLEND_ZERO`: **F = (0, 0, 0, 0)**
- `D3D12_BLEND_ONE`: **F = (1, 1, 1, 1)**
- `D3D12_BLEND_SRC_COLOR`: **F = (r<sub>src</sub>, g<sub>src</sub>, b<sub>src</sub>)**
- `D3D12_BLEND_INV_SRC_COLOR`: **F<sub>src</sub> = (1 - r<sub>src</sub>, 1 - g<sub>src</sub>, 1 - b<sub>src</sub>)**
- `D3D12_BLEND_SRC_ALPHA`: **F = (a<sub>src</sub>, a<sub>src</sub>, a<sub>src</sub>, a<sub>src</sub>)**
- `D3D12_BLEND_INV_SRC_ALPHA`: **F = (1 - a<sub>src</sub>, 1 - a<sub>src</sub>, 1 - a<sub>src</sub>, 1 - a<sub>src</sub>)**
- `D3D12_BLEND_DEST_ALPHA`: **F = (a<sub>dst</sub>, a<sub>dst</sub>, a<sub>dst</sub>, a<sub>dst</sub>)**
- `D3D12_BLEND_INV_DEST_ALPHA`: **F = (1 - a<sub>dst</sub>,1 - a<sub>dst</sub>, 1 - a<sub>dst</sub>, 1 - a<sub>dst</sub>)**
- `D3D12_BLEND_DEST_COLOR`: **F = (a<sub>dst</sub>, a<sub>dst</sub>, a<sub>dst</sub>)**
- `D3D12_BLEND_INV_DEST_COLOR`: **F = (1 - a<sub>dst</sub>, 1 - a<sub>dst</sub>, 1 - a<sub>dst</sub>)**
- `D3D12_BLEND_SRC_ALPHA_SAT`: **F = (a'<sub>src</sub>, a'<sub>src</sub>, a'<sub>src</sub>, a'<sub>src</sub>), a'<sub>src</sub> = clamp(a<sub>src</sub>, 0, 1)**
- `D3D12_BLEND_BLEND_FACTOR`: **F = (r, g, b, a)**

最后一个枚举类型中的参数 **(r ,g ,b ,a)** 通过下面这个函数设置。

`ID3D12GraphicsCommandList::OMSetBlendFactor`

参数是一个`Float[4]`，表示4个分量的值，如果设置为`nullptr`那么就默认全是1。

## 10.4 BLEND STATE

我们已经讨论过了混合操作符和混合因素，但是我们如何在`Direct3D`里面设置这些参数呢？
和其他的`Direct3D`的状态一样，混合状态也是`PSO(渲染管道)`的一个部分。
之前我们使用的都是默认的混合状态(禁用状态)。

我们如果要使用非默认的混合状态，我们必须填充`D3D12_BLEND_DESC`结构。

```C++
    struct D3D12_BLEND_DESC{
        bool AlphaToCoverageEnable; //默认是False
        bool IndependentBlendEnable; //默认是False
        D3D11_RENDER_TARGET_BLEND_DESC RenderTarget[8];
    };
```

- `AlphaToCoverageEnable`:设置成`true`开启`alpha-to-coverage`技术，这个技术是多重采样技术在渲染某些纹理 **(这里的翻译无法保证正确性，因此就使用某些纹理代替)** 的时候使用的。设置成`false`来关闭这个技术。`alpha-to-coverage`技术需要多重采样开启才能使用(换言之就是必须在创建后台缓冲和深度缓冲的时候开启多重采样)。
- `IndependentBlendEnable`:`Direct3D`最多支持同时渲染8个`Render Target`。如果这个属性设置成`true`，那么就可以在渲染不同的'Render Target'的时候使用不同的混合参数(例如混合因素，混合操作符，混合是否开启等)。如果设置成`false`，那么所有的`Render Target`就会使用同样的混合方法(具体来说就是`D3D12_BLEND_DESC::RenderTarget`中的第一个元素作为所有的`Render Target`使用的混合方法)。对于现在来说，我们一次只使用一个`Render Target`。
- `RenderTarget`:第i个元素描述第i个`Render Target`使用的混合方法，如果`IndependentBlendEnable`设置成`false`，那么所有的`Render Target`就全部使用`RenderTarget[0]`这个混合方法去进行混合。









