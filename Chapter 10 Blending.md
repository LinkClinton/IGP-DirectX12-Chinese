# <span id = "10"> Chapter 10 Blending </span>

观察下方图片[10.1](#Image10.1)。
我们在这一帧中最开始渲染的是地形和木箱，因此地形和木箱的像素就被储存在后台缓冲中。
然后我们使用混合技术来绘制一个水面到后台缓冲，因此水的像素和地形以及木箱的像素在后台缓冲中得到了混合，看起来就是木箱和地形穿过了水面。
在本章中，我们尝试混合技术，这个技术能够就是混合(组合)现在正在光栅化的像素(我们称之为源)和之前已经完成光栅化并存储在后台缓冲中的像素(我们称之为目标)。
这个技术能够让我们去渲染透明的物体，例如水和玻璃。

<img src="Images/10.1.png" id = "Image10.1"> </img>

**目标**

- 理解如何使用混合，并且能够在`Direct3D`中使用它。
- 学习`Direct3D`支持的不同的混合模式。
- 发现如何通过使用Alpha去控制图元的透明度。
- 学习如何使用HLSL中的Clip函数阻止一个像素绘制到后台缓冲中。

## <span id = "10.1">  10.1 THE BLENDING EQUATION </span>

我们设**C<sub>src**</sub>表示从我们的像素着色器(**PixelShader**)输出的第**i**,**j**个像素，也就是我们正在光栅化的像素，然后我们设**C<sub>dst**</sub>表示现在在后台缓冲中第**i**,**j**个像素。
如果不使用混合技术的话，像素**C<sub>src**</sub>将会替代**C<sub>dst**</sub>(前提是他能够通过深度和模板测试)。
但是在使用混合的情况下，**C<sub>src**</sub>和**C<sub>dst**</sub>将会混合成一个新的颜色**C**，并且**C**将会替代**C<sub>dst**</sub>作为后台缓冲里面的像素(你可以认为新的颜色**C**将会被写入到后台缓冲中去)。
`Direct3D`使用下面的这个方程来混合源和目标像素的颜色:

**<center>C = C<sub>src</sub> × F<sub>src</sub> ^ C<sub>dst</sub> × F<sub>dst</sub></center>**

F将会在下面介绍，主要是通过F来让我们有更多的方式去实现更多的效果。
`×` 符合表示的是向量的点积，`^`(他那个符合我打不出，我们暂且叫做混合操作)符号是一种由我们自主定义的运算，具体下面会介绍。

上面的方程是用于处理颜色分量中的**RGB**的，对于**Alpha**值我们单独使用下面的方程处理，这个方程和上面的是极为相似的：

**<center>A = A<sub>src</sub>F<sub>src</sub> ^ A<sub>dst</sub>F<sub>dst</sub></center>**

这个方程基本上是一样的，但是这样分开处理的话就可以让`^`运算可以不同了。我们将RGB和Alpha分开处理的动机就是让我们能够单独处理RGB和Alpha值，而两者不互相影响。


## <span id = "10.2"> 10.2 BLEND OPERATIONTS </span>

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
## <span id = "10.3"> 10.3 BLEND FACTORS </span>

通过改变`Factors(因素)`，我们可以设置更多的不同的混合组合，从而来实现更多的不同的效果。
我们将会在下面解释一些混合组合，但是你还是要去体验一下他们的效果，从而能够有一个概念。
下面将会介绍一些基础的`Factors`。你可以去看**SDK**文档里面的`D3D12_BLEND`枚举了解到更多高级的`Factors`。
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

## <span id = "10.4"> 10.4 BLEND STATE </span>

我们已经讨论过了混合操作符和混合因素，但是我们如何在`Direct3D`里面设置这些参数呢？
和其他的`Direct3D`的状态一样，混合状态也是`PSO(渲染管道)`的一个部分。
之前我们使用的都是默认的混合状态(禁用状态)。

我们如果要使用非默认的混合状态，我们必须填充`D3D12_BLEND_DESC`结构。

```C++
    struct D3D12_BLEND_DESC{
        bool AlphaToCoverageEnable; // false
        bool IndependentBlendEnable; // false
        D3D11_RENDER_TARGET_BLEND_DESC RenderTarget[8];
    };
```

- `AlphaToCoverageEnable`:设置成`true`开启`alpha-to-coverage`技术，这个技术是多重采样技术在渲染某些纹理 **(这里的翻译无法保证正确性，因此就使用某些纹理代替)** 的时候使用的。设置成`false`来关闭这个技术。`alpha-to-coverage`技术需要多重采样开启才能使用(换言之就是必须在创建后台缓冲和深度缓冲的时候开启多重采样)。

- `IndependentBlendEnable`:`Direct3D`最多支持同时渲染8个`Render Target`。如果这个属性设置成`true`，那么就可以在渲染不同的`Render Target`的时候使用不同的混合参数(例如混合因素，混合操作符，混合是否开启等)。如果设置成`false`，那么所有的`Render Target`就会使用同样的混合方法(具体来说就是`D3D12_BLEND_DESC::RenderTarget`中的第一个元素作为所有的`Render Target`使用的混合方法)。对于现在来说，我们一次只使用一个`Render Target`。

- `RenderTarget`:第i个元素描述第i个`Render Target`使用的混合方法，如果`IndependentBlendEnable`设置成`false`，那么所有的`Render Target`就全部使用`RenderTarget[0]`这个混合方法去进行混合。


`D3D12_RENDER_TARGET_BLEND_DESC`结构如下所示:

```C++
    struct D3D12_RENDER_TARGET_BLEND_DESC{
        bool BlendEnable; // false
        bool LogicOpEnable; // false
        D3D12_BLEND SrcBlend; // D3D12_BLEND_ONE
        D3D12_BLEND DestBlend; // D3D12_BLEND_ZERO
        D3D12_BLEND_OP BlendOp; // D3D12_BLEND_OP_ADD
        D3D12_BLEND SrcBlendAlpha; // D3D12_BLEND_ONE
        D3D12_BLEND DestBlendAlpha; // D3D12_BLEND_ZERO
        D3D12_BLEND_OP BlendOpAlpha // D3D12_BLEND_OP_ADD
        D3D12_LOGIC_OP LogicOp; // D3D12_LOGIC_OP_NOOP
        UINT8 RenderTargetWriteMask; // D3D12_COLOR_WRITE_ENABLE_ALL
    };
```

- `BlendEnable`: 设置成`true`就开启混合否则就是关闭，注意的是`LogicOpEnable`和`BlendEnable`不能同时开启，你必须使用其中的一个来进行混合。
- `LogicOpEnable`: 设置成`true`就开启使用逻辑运算符的混合，然后和`BlendEnable`不能同时使用。
- `SrcBlend`: **RGB**混合中的**F<sub>src</sub>**。
- `DestBlend`:  **RGB**混合中的**F<sub>dst</sub>**。
- `BlendOp`: **RGB**混合中使用的操作符。
- `SrcBlendAlpha`: **Alpha**混合中的**F<sub>src</sub>**。
- `DestBlendAlpha`: **Alpha**混合中的**F<sub>dst</sub>**。
- `BlendOpAlpha`: **Alpha**混合中使用的操作符。
- `LogicOp`: 混合中使用的逻辑运算符。
- `RenderTargetWriteMask`: 用于控制混合结束后哪些颜色(**R,G,B,A**)可以写入到后台缓冲中去。举个例子来说就是如果我们想禁止将**RGB**写入到后台缓冲中去的话，我们就可以设置成`D3D12_COLOR_WRITE_ENABLE_ALPHA`。如果混合是关闭的，那么就没有任何限制输出到后台缓冲中去。

**Notice:** 由于混合需要处理每一个像素，所以他的开销很大。你最好只在需要的时候才打开它。

## <span id = "10.5"> 10.5 EXAMPLES </span>

在这个部分，我们看一些混合操作的特效例子。当然我们只看关于**RGB**混合的例子。

### <span id = "10.5.1"> 10.5.1 No Color Write </span>

如果我们只是想单纯的留下目标像素，即源像素不会和目标像素进行混合以及覆盖，那么就可以使用这个方法。
举个例子来说就是，将目标像素输出到`Depth/Stencil Buffer`中去。方程在下面：

**<center>C = C<sub>src</sub> × (0, 0, 0) + C<sub>dst</sub> × (1, 1, 1)</center>**

**<center>C = C<sub>dst</sub></center>**

另外一个方法就是将`RenderTargetWriteMask`设置成0。
这样的话就禁止了所有的颜色输出到`Back Buffer`中。


### <span id = "10.5.2"> 10.5.2 Adding/Subtracting </span>

<img src = "Images/10.2.png" id = "Image10.2"></img>

如果我们想将源像素和目标像素加起来(参见[10.2](#Image10.2))。方程如下：

**<center>C = C<sub>src</sub> × (1, 1, 1) + C<sub>dst</sub> × (1, 1, 1)</center>**

**<center>C = C<sub>src</sub> + C<sub>dst</sub></center>**

<img src = "Images/10.3.png" id = "Image10.3"></img>


我们当然也可以相减啊(参见[10.3](#Image10.3))。方程如下：

**<center>C = C<sub>src</sub> × (1, 1, 1) - C<sub>dst</sub> × (1, 1, 1)</center>**

**<center>C = C<sub>src</sub> - C<sub>dst</sub></center>**

### <span id = "10.5.3"> 10.5.3 Multiplying </span>

<img src = "Images/10.4.png" id = "Image10.4"></img>

如果我们想将源像素和目标像素相乘(参见[10.4](#Image10.4))。方程如下：

**<center>C = C<sub>src</sub> × (0, 0, 0) x C<sub>dst</sub> × C<sub>src</sub></center>**

**<center>C = C<sub>src</sub> x C<sub>dst</sub></center>**

### <span id = "10.5.4"> 10.5.4 Transparency </span>

现在我们假设**Alpha**分量用来控制源像素的不透明度(0就是**0%**,0.4就是**40%**)。
我们设不透明度为**A**，透明度为**T**。那么透明度和不透明度的关系就是**T = 1 - A**。
比如不透明度是0.4,那么透明度就是0.6。现在我们想将源像素和目标像素在保留源像素的不透明度的情况下，将目标像素透明。方程如下：

**<center>C = C<sub>src</sub> × (a<sub>src</sub>, a<sub>src</sub>, a<sub>src</sub>) + C<sub>dst</sub> × (1 - a<sub>src</sub>, 1 - a<sub>src</sub>, 1 - a<sub>src</sub>)</center>**

**<center>C = a<sub>src</sub> × C<sub>src</sub> + (1 - a<sub>src</sub>) × C<sub>dst</sub></center>**

举个例子就是，我们假设**a<sub>src</sub> = 0.25**，就是不透明度为**25%**。
当源像素和目标像素混合的时候，我们希望保留 **25%** 的源像素，**75%** 的目标像素(这里目标像素在源像素的前面，其实就是说决定目标像素的物体在决定源像素的物体前面)。方程如下：

**<center>C = C<sub>src</sub> × (a<sub>src</sub>, a<sub>src</sub>, a<sub>src</sub>) + C<sub>dst</sub> × (1 - a<sub>src</sub>, 1 - a<sub>src</sub>, 1 - a<sub>src</sub>)</center>**

**<center>C = 0.25 × C<sub>src</sub> + 0.75 × C<sub>dst</sub></center>**

通过使用混合的方法，我们就可以绘制如[10.1](#Image10.1)的物体了。这里你就需要在混合的时候注意一些东西，否则你就会绘制的时候出现问题。
我们必须遵守如下规则：

**首先绘制那些不需要混合的物体。
然后将需要混合的物体按照他们和摄像机的距离排序。
然后按照从后往前的顺序绘制物体。**

从后往前绘制物体的原因我不晓得如何用中文描述了，这个我觉得很显然啊。所以下面是我的**BB**：

对于一个物体来说，我们要将他进行混合的话，我们保留的是后面的像素，因此我们需要先绘制保留的像素，然后在绘制其他的像素。

对于[**10.5.1**](#10.5.1)，绘制的顺序已经没有意义了，反正不会输出。对于[**10.5.2**](#10.5.2)和[**10.5.3**](#10.5.3)我们仍然先绘制不需要混合的物体，然后绘制需要混合的物体。
这是因为我们需要在开始混合之前将所有的不进行混合的像素确定下来。在这里我们并不需要排序需要混合的物体。因为这个运算是满足交换律的。我们设源像素为**B**。

**<center>B' = B + C<sub>0</sub> + ... + C<sub>n-1</sub></center>**

**<center>B' = B - C<sub>0</sub> + ... - C<sub>n-1</sub></center>**

**<center>B' = B ^ C<sub>0</sub> + ... ^ C<sub>n-1</sub></center>**

### <span id = "10.5.5"> 10.5.5 Blending and the Depth Buffer </span>

当我们进行前面说的几种混合(不包括第一种)的时候，在深度测试的时候可能会有一点问题。
这里我们以加法混合作为例子，其他的混合是差不多的思路。

原文说了那么多其实就是想告诉你如果你开启了深度测试的话，你不按照从后往前的顺序绘制的话，那么就可能有像素因为深度测试而丢弃，从而没有累加到混合的方程中去，导致最后的颜色有点小问题。
因此我就不直接翻译原文了(原文里面有一部分单词语法没理解，我英语是个渣，但是意思是这个意思没错)。


## <span id = "10.6"> 10.6 ALPHA CHANNELS </span>

从[**10.5.4**](#10.5.4)中我们使用**Alpha**分量在**RGB**混合中去控制物体的不透明度。
用于混合的源像素的颜色来自像素着色器。
回顾上一个章节，我们返回`Diffuse`材质的**Alpha**值作为像素着色器输出的**Alpha**值。
因此`Diffuse Map`的**Alpha**通道的值就是用于透明度的。

你可以使用图片编辑软件(例如PS)给任何图片加入**Alpha**通道，然后将图片存储为支持**Alpha**通道的图片格式，例如**DDS**。

## <span id = "10.7"> 10.7 CLIPPING PIXELS </span>

有时候我们想从正在处理的源像素中完全剔除一部分像素。
我们可以通过时候`HLSL`内置的函数`Clip(x)`(**这个函数只能在像素着色器中使用**)。
这个函数在**x < 0**的时候将会丢弃现在正在处理的像素，即这个像素不会被绘制到后台缓冲中去，也不会进行之后的一系列处理。
这个方法通常用于绘制电线或者篱笆贴图。参见[10.6](#Image10.6)。我们可以通过这样的方法绘制的时候一些地方不透明一些地方透明。

<img src = "Images/10.6.png" id = "Image10.6"></img>

```HLSL
float4 PS(VertexOut pIn) : SV_TARGET
{
    clip(pIn.color.a - x); //如果当前像素的Alpha小于x，那么就剔除他。
    return pIn.color; //返回颜色。
}
```

注意的是`clip`开销也是有的，所以建议只在需要使用的时候使用。

我们可以使用混合做到同样的效果，但是这种方法相比较来说更为有效。
对于一个被剔除的像素来说，之后的关于他的操作会被跳过(例如混合，深度测试什么的)。

图片[10.7](#Image10.7)显示了一个混合例子。
他使用透明混合来绘制半透明的水，使用剔除测试(`Clip Test`)来绘制栅栏盒。
值得注意的是，由于我们可以透过盒子看到盒子的背面，所以我们要关闭背面剔除。

<img src = "Images/10.7.png" id = "Image10.7"></img>


## <span id = "10.8"> 10.8 FOG</span>

为了在游戏中模仿准确的天气环境，我们需要能够实现一个雾的特效。
参见图片[10.8](#Image10.8)。可以显然看出雾的效果。
雾可以遮掩原处的物体，并且阻止`Popping`。
`Popping`就是当一个物体原本在可视范围(`Far Plane`)外的时候，然后因为摄像机的移动导致这个物体移动到了可视范围(`Frustum`)内，因此这个物体就可以被看见。
这样物体突然出现，会有一种比较奇怪的感觉。
但是如果使用雾层的话，那么远处的物体即使出现也会因为雾的效果模糊，从而不会显得那么突然。
注意即使你的场景发生在晴天，你也最好在远处保持一层雾层，因为即使在晴天，远处的物体的出现和消失也是一个和距离有关的函数。我们可以使用雾来模仿这一个大气环境现象。

<img src = "Images/10.8.png" id = "Image10.8"></img>

我们实现雾的方法：我们需要确定雾的颜色，雾的起始位置距离摄像机多远，雾的范围(这个范围从雾的起始点开始到完全遮掩物体)。
在三角形上面的一个点的颜色是一个权重的平均值：

<img src = "Images/10.9.png" id = "Image10.9"></img>

 **<center>foggedColor = litColor + s(fogColor - litColor)</center>**
 
 **<center>foggedColor = (1 - s) × litColor + s × fogColor</center>**

 参数**s**的范围在 **[0,1]** 之间他是一个关于摄像机到物体某一个面上面的一个点的距离的函数。
 随着距离的逐渐增大，这个点会逐渐被雾遮住。**s**的定义：

 **<center>s = saturate((dist(p,E) - fogStart) / fogRange)</center>**

 **dist(p,E)** 表示的是摄像机到点的距离。**saturate** 将参数保持在 **[0,1]** 范围内(**大于1就是1，小于0就是0，否则就是原本的值**)。(看图都能看明白...)

 图片[10.10](#Image10.10)就绘制了这个函数**s**。我们可以看到当**dist(p, E) <= fogStart**的时候，**s = 0**，并且最终的颜色就等于原本的颜色了(**foggedColor = litColor**)。

<img src = "Images/10.10.png" id = "Image10.10"></img>


换句话来说，雾并没有修改距离摄像机小于**fogStart**的顶点的颜色。
雾只会对那些距离摄像机大于**fogStart**的物体起作用。

我们设**fogEnd = fogStart + fogRange**。当**dist(p, E) >= fogEnd,s = 1**的时候最终的颜色就是雾的颜色了(**foggedColor = fogColor**)。

换句话来说，雾完全遮住了距离摄像机大于等于**FogEnd**的点的颜色，所以你只能看见雾的颜色。

当**FogStart < dist(p, E) < fogEnd**的时候，我们可以看到**s**随着 **dist(p, E)** 的增长而线性增长。
这意味着，当距离越来越远的时候，雾的颜色在最后的颜色中占的比重越来越大，原本的颜色占的比重越来越小了。
当然，随着距离越来越远，雾造成的模糊越来越剧烈。

...省略下面的代码部分。

有些场景并不想使用雾，我们可以定义一个宏定义来在编译着色器的时候决定是否开启雾效。
这样的话，如果我们不想使用雾效的话，就不会产生额外的运算开销了。具体参见`D3D_SHADER_MACRO`。


## <span id = "10.9"> 10.9 SUMMARY</span>

- 混合是一项能够让我们将正在处理的像素(**Source Pixel**)和已经处理好的像素(**Destination Pixel**)进行混合的技术。
- 混合是有一个混合方程的，注意的是**RGB**和**Alpha**混合是独立的。
- **F<sub>src</sub>, F<sub>dst</sub>...** 称作混合因素(`Blend Factors`)，他提供了方法让我们自己定义混合方程。对于**Alpha**混合是不能使用带有 **_COLOR** 关键字的参数。
- 源**Alpha**值来自于漫反射材质。在我们的框架中，漫反射材质定义为一张纹理，并且纹理的**Alpha**通道存储了**Alpha**信息。
- 源像素可以通过使用`HLSL`函数`Clip(x)`来将其丢弃，从而不对其进行进一步处理。这个函数只能在像素着色器里使用，如果**x < 0**的话，那么现在处理的像素就会被丢弃。
- 使用雾来模拟各种各样的天气和大气远景。在我们的线性雾模型中，我们定义一个雾的颜色，一个雾的起始点(距离摄像机的距离)，一个雾的范围。一个面上的点的颜色将使用方程来计算他的颜色。



终于写完了。虽然感觉和原版差距好大。但是我觉得应该能够看懂吧？**2333**。
感觉原版的书及其啰嗦啊，虽然很厉害就是了。

