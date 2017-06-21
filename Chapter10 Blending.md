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

**C = C<sub>src</sub> × F<sub>src</sub> ^ C<sub>dst</sub> × F<sub>dst</sub>**

F将会在下面介绍，主要是通过F来让我们有更多的方式去实现更多的效果。
`×` 符合表示的是向量的点积，`^`(他那个符合我打不出，我们暂且叫做混合操作)符号是一种由我们自主定义的运算，具体下面会介绍。

上面的方程是用于处理颜色分量中的RGB的，对于Alpha值我们单独使用下面的方程处理，这个方程和上面的是极为相似的：

**A = A<sub>src</sub>F<sub>src</sub> ^ A<sub>dst</sub>F<sub>dst</sub>**

这个方程基本上是一样的，但是这样分开处理的话就可以让`^`运算可以不同了。我们将RGB和Alpha分开处理的动机就是让我们能够单独处理RGB和Alpha值，而两者不互相影响。


## 10.2 BLEND OPERATIONTS

- D3D12_BLEND_OP_ADD： C = C<sub>src</sub> × F<sub>src</sub> + C<sub>dst</sub> × F<sub>dst</sub>
- D3D12_BLEND_OP_SUBTRACT： C = C<sub>dst</sub> × F<sub>dst</sub> - C<sub>src</sub> × F<sub>src</sub>
- D3D12_BLEND_OP_REV_SUBTRACT： C = C<sub>src</sub> × F<sub>src</sub> - C<sub>dst</sub> × F<sub>dst</sub> 
- D3D12_BLEND_OP_MIN： C = min(C<sub>src</sub>, C<sub>dst</sub>)
- D3D12_BLEND_OP_MAX： C = max(C<sub>src</sub>, C<sub>dst</sub>)

Alpha的混合操作也是一样的。
当然你可以使用不同的操作来分别处理RGB和Alpha的混合。
举个例子来说，你可以在RGB的混合中使用`+`，然后在Alpha的混合中使用`-`。

**C = C<sub>src</sub> × F<sub>src</sub> + C<sub>dst</sub> × F<sub>dst</sub>** 

**A = A<sub>dst</sub>F<sub>dst</sub> - A<sub>src</sub>F<sub>src</sub>**


最近在`Direct3D`中加入了一个新的特征，我们可以使用逻辑运算符来代替上面的混合操作。
具体的我就没必要放进去了，毕竟很简单理解。

但是你需要注意的是，如果你使用逻辑运算符代替混合操作，你需要注意你的`Render Target`的格式是否支持这个运算了。
并且你不能同时使用逻辑运算符和传统的混合运算符。两者只能选择一个同时使用。

## 10.3 BLEND FACTORS

通过改变`Factors`我们可以设置更多的不同的混合组合，从而来实现更多的不同的效果。
我们将会在下面解释一些混合组合，但是你还是要去体验一下他们的效果，从而能够有一个概念。
下面将会介绍一些基础的`Factors`。

思考了下，这东西显然可以去看原书啊，我还是不在这里描述了，因为内容全是运算符合啥的。

`ID3D12GraphicsCommandList::OMSetBlendFactor`可以设置`Factors`。
如果设置成`nullptr`的话，那么就默认全是1了。


这里需要注意下，就是`Factors`并不是支持所有的混合方程，如果带有_COLOR的，那么他就只支持RGB的混合，Alpha的混合是不支持的。你可以认为Alpha的混合直接忽略。

`Clamp(x, a, b)`函数就是返回一个值在`[a,b]`范围内，如果`x`在范围内返回就是`x`，否则就是`a,b`中和`x`最接近的。

