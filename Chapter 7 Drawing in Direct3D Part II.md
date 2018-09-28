# Chapter 7 DRAWING IN DIRECT3D PART II

这一章节我们将会介绍一些会在本书剩余部分使用的渲染模式。
章节最开始，我们将会介绍一个关于渲染优化的东西，一个叫做`帧资源(Frame Resources)`的东西。具体来说就是我们通过一些方法来避免在每一帧中刷新指令队列，及尽量减少同步`CPU`和`GPU`使得我们能够充分使用他们。之后我们介绍一下关于分项渲染的概念。之后，我们会了解更多关于来源标记的细节，以及学习另外两个参数类型，描述符(`root descriptors`)和常量(`root constants`)。最后，我们将会绘制一些复杂的物体。

> 目标：
- 了解如何修改我们的渲染过程来避免每一帧都刷新指令队列，从而提升我们的程序效率。
- 了解另外两个来源标记的参数类型，描述符和常量。
- 了解如何生成和渲染一些基础的物体，例如网格，球体等。
- 了解如何使用`CPU`去改变顶点数据，然后使用`GPU`更新到我们的缓冲中去。

## 7.1 FRAME RESOURCES

回顾4.2，我们知道`GPU`和`CPU`的运行是互相独立的，即平行的，`CPU`构建和提交指令列表，`GPU`处理指令队列里面的指令。而我们的目的就是保持`CPU`和`GPU`不断的运行，从而能够充分使用硬件资源。在之前我们的例子中，我们会在每一帧结束的时候同步`GPU`和`CPU`，下面有两个这样做的理由。

- 在`GPU`没有执行完所有的指令队列的时候指令分配器是不能够重置的。假设我们不同步他们的话，那么`CPU`可能就在`GPU`还没有处理完第$n$帧的指令的时候就开始处理第$n+1$帧的内容，那么如果在第$n+1$帧的时候，`CPU`重置指令分配器的话，`GPU`还在处理第$n$帧的指令，那么`GPU`还没有处理的指令就会被清空。
- 如果一个常缓冲会在一个渲染指令中使用的话，那么在`GPU`执行完这个指令前是不能够使用`CPU`更新它的。在4.22中我们提到过，假设我们不同步的话，`CPU`可能在第$n+1$帧的时候更新我们的常缓冲，但是`GPU`却还没有执行第$n$帧中使用了这个常缓冲的渲染指令的话，那么当`GPU`执行到这个指令的时候，常缓冲里面的数据就已经不是第$n$帧的数据而是第$n+1$帧的数据了。

因此我们非常有必要在每帧的结束的时候同步我们的`CPU`和`GPU`，但是这样做的话，会浪费我们的效率。

- 在这一帧循环刚开始的时候可能`GPU`可能没有任何任务需要处理，要等到`CPU`提交指令列表后才可以处理。
- 在这一帧循环结束的时候，我们的`CPU`要等待我们的`GPU`执行完这一帧的所有的指令。

简单来说这样做的话在每一帧都会有一段时间`CPU`或者`GPU`处于空闲阶段。

因此我们就有了一个解决的方法，就是创建一个存有每一帧`CPU`要修改的资源环型数组。我们称这样的资源叫做帧资源。通常这个环型数组的大小我们是定位3就好了。当你`CPU`处理到第$n$帧的时候，而`GPU`还没有处理到，`CPU`可以通过我们创建的帧资源数组来提前处理下一帧的资源，以及构建指令列表等。当到底数组末尾的时候，如果`GPU`还没有处理完数组开始所代表的那一帧的内容，就等待他完成，否则就直接将数组开始接到数组末尾，这样不断循环下去。

```C++
///Code
```

这样做的话，我们虽然还是需要进行两个处理器的同步工作，但是相比来说有很大的改善。
因为我们在`GPU`还在处理第$n$帧的时候就帮他构建好了之后的指令列表，因此只要`GPU`和`CPU`的差距不是太大，那么`GPU`应该会不间断的运行，然后`CPU`可能会偶尔跑的太快要等待`GPU`处理完，这个时候你还可以用等待的额外时间去计算另外的东西。

## 7.2 RENDER ITEMS

我们在绘制一个物体的时候通常需要设置很多参数，例如要绑定的顶点和索引缓冲，常缓冲，基础图元类型等。
当我们在绘制多个物体的时候，为了简便，我们可以定义一个轻量的结构体来存储我们要绘制的一个物体的数据。
其实就是定义一个结构体来存储一些关于我们要绘制的物体的信息，使得我们在编写代码上能更加直观的编写。
比如这样的例子。

```C++
struct RenderItem{
    int VertexCount;
    int IndexCount;
    int StartVertexLocation;
    int StartIndexLocation;
    //...
};
```

当然我们还可以在里面加入一些数据，这些都是要看具体情况的，你只需要有这样的一个概念就好了。

## 7.3 PASS CONSTANTS

在渲染一个物体的时候，可能我们会在着色器中用到一些其他的信息，例如摄像机的位置，渲染目标的大小等等，因此这里我们就将这些信息都存放在一个常缓冲中，每次绘制一个物体之前就只需要更新一次缓冲就好了。当然具体情况具体分析，这样做并不代表它有什么优势。只是在不追求效率的情况下稍微方便编写代码一些。

## 7.4 SHAPE GEOMETRY

其实主要想法就是将一个模型的网格信息抽象成一个类，即我们用一个类来保存我们的模型的网格的顶点以及索引信息等。

并且之后的内容也只是教你如何使用代码生成一些简单的物体，例如球体，圆台等物体。如果感兴趣可以去看原文。

## 7.5 SHAPES DEMO

这里就是原文的例子的介绍了。主要是介绍了之前讲的内容的应用。直接去看实例代码就好了。

## 7.6 MORE ON ROOT SIGNATURES

我们之前在6.6.5中介绍了什么是来源标记(`Root Signatures`)。它定义了我们在渲染之前要绑定到渲染管线的资源类型，以及将这些资源类型和着色器的输入寄存器一一映射。具体绑定的资源就要看具体需要什么资源了，这里只是规定了资源的类型(例如`CBV`,`SRV`,`UAV`等)。并且当我们创建一个渲染管线状态的时候，我们会验证这个渲染管线状态中的来源标记和着色器是否能够互相吻合。

### 7.6.1 Root Parameters

我们知道一个来源标记能够有很多个参数，之前我们只是定义了一个参数作为描述符表来使用。这里将介绍来源标记的参数支持的类型。

- `Descriptor Table`: 描述符表，能够支持绑定一个堆里面的一个范围内的资源。
- `Root Descriptor`: 描述符，能够直接绑定资源，也就是说资源并不一定要求在堆里面，但是只支持缓冲类型。也就是说你能够使用`CBV`，但如果你使用`SRV`或者`UAV`的话他们就必须被当作一组缓冲使用，而不能被当作纹理使用。
- `Root Constant`: 直接绑定一个$32bit$大小的常量。

由于性能原因，一个来源标记的大小不能超过`64 DWORD`，而不同类型的参数有不同的大小消耗。

- `Descriptor Table`: 每个消耗`1 DWORD`。
- `Root Descriptor`: 每个消耗`2 DWORD`。
- `Root Constant`: 每个消耗`1 DWORD`。

只要我们创建的来源标记的大小不超过限制，那么如何定义就是随你的意了。

```C++
struct D3D12_ROOT_PARAMETER
{
    D3D12_ROOT_PARAMETER_TYPE ParameterType;
    union
    {
            D3D12_ROOT_DESCRIPTOR_TABLE DescriptorTable;
            D3D12_ROOT_CONSTANTS Constants;
            D3D12_ROOT_DESCRIPTOR Descriptor;
    }
    D3D12_SHADER_VISIBILITY ShaderVisibility;
};
```

- `ParameterType`: 参数类型，支持的参数大致就是描述符表，常量，`CBV`,`SRV`,`UAV`类型的描述符。
- `DescriptorTable/Constants/Descriptor`: 这里如果你不知道什么是`union`请先去学习C++的语法再说。具体你该填充哪个参数就要看你选择的参数类型是什么了。
- `ShaderVisibility`: 指定我们这个参数对着色器的可见性。这里我们默认使用`D3D12_SHADER_VISIBILITY_ALL`，如果你只是在像素着色器中使用这个参数的话，那么你也可以指定`D3D12_SHADER_VISIBILITY_PIXEL`来限制我们只能够在像素着色器中使用这个参数。不过限制在一些着色器中使用的话可以优化一些性能。

```C++
enum D3D12_SHADER_VISIBILITY{
    D3D12_SHADER_VISIBILITY_ALL = 0,
    D3D12_SHADER_VISIBILITY_VERTEX = 1,
    D3D12_SHADER_VISIBILITY_HULL = 2,
    D3D12_SHADER_VISIBILITY_DOMAIN = 3,
    D3D12_SHADER_VISIBILITY_GEOMETRY = 4,
    D3D12_SHADER_VISIBILITY_PIXEL = 5
}
```

> **这里我不确保这些参数可以使用异或或者什么方式组合。**

### 7.6.2 Descriptor Tables

```C++
struct D3D12_ROOT_DESCRIPTOR_TABLE
{
    UINT NumDescriptorRanges;
    const D3D12_DESCRIPTOR_RANGE *pDescriptorRanges;
};

struct D3D12_DESCRIPTOR_RANGE
{
    D3D12_DESCRIPTOR_RANGE_TYPE RangeType;
    UINT NumDescriptors;
    UINT BaseShaderRegister;
    UINT RegisterSpace;
    UINT OffsetInDescriptorsFromTableStart;
};

enum D3D12_DESCRIPTOR_RANGE_TYPE
{
    D3D12_DESCRIPTOR_RANGE_TYPE_SRV = 0,
    D3D12_DESCRIPTOR_RANGE_TYPE_UAV = 1,
    D3D12_DESCRIPTOR_RANGE_TYPE_CBV = 2,
    D3D12_DESCRIPTOR_RANGE_TYPE_SAMPLER = 3
};
```

- `RangeType`: 包含的一组描述符的类型。
- `NumDescriptors`: 这一组的描述符个数。
- `BaseShaderRegister`: 从哪个着色器寄存器开始以此往后推。假设你的描述符类型是`CBV`，你设置3个描述符并且你的`BaseShaderRegister`是1的话，那么它在着色器中就对应下面的三个常缓冲。
    ```hlsl
        cbuffer cbA : register(b1) {...};
        cbuffer cbB : register(b2) {...};
        cbuffer cbC : register(b3) {...};
    ```
- `RegisterSpace`: 用于进一步区分，如果我们有两组描述符的`BaseShaderRegister`是一样的话，我们可以通过使用不同的`RegisterSpace`来将他们区分开来。例如我有两个纹理他的着色器输入寄存器都是0的话，但是他们的寄存器空间不同。如果不指定寄存器空间的话就默认为0。
    ```hlsl
        Texture2D normalMap1 : register(t0, space1);
        Texture2D normalMap2 : register(t0, space2);
    ```
- `OffsetInDescriptorsFromTableStart`: 这一组描述符距离描述符表的起始位置的偏差值。具体参见样例。

```C++
    D3D12_DESCRIPTOR_RANGE range[3];
    range[0].RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_CBV;
    range[0].NumDescriptors = 2;
    range[0].BaseShaderRegister = 0;
    range[0].RegisterSpace = 0;
    range[0].OffsetInDescriptorsFromTableStart = 0;

    range[1].RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_SRV;
    range[1].NumDescriptors = 3;
    range[1].BaseShaderRegister = 0;
    range[1].RegisterSpace = 0;
    range[1].OffsetInDescriptorsFromTableStart = 2;

    range[2].RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_UAV;
    range[2].NumDescriptors = 1;
    range[2].BaseShaderRegister = 0;
    range[2].RegisterSpace = 0;
    range[2].OffsetInDescriptorsFromTableStart = 5;

    D3D12_ROOT_DESCRIPTOR_TABLE table;
    table.NumDescriptorRanges = 3;
    table.pDescriptorRanges = range;
```

上面的例子就创建了一个存储两个`CBV`然后3个`SRV`然后一个`UAV`的描述符表。然后关于`OffsetInDescriptorsFromTableStart`这个参数，我们也可以将其交给`Direct3D`自己去计算，你只需要将这个变量的值设为`D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND`就可以了。

### 7.6.3 Root Descriptors

```C++
struct D3D12_ROOT_DESCRIPTOR
{
    UINT ShaderRegister;
    UINT RegisterSpace;
};
```

- `ShaderRegister`: 描述符要绑定到着色器的哪个寄存器。例如你设置为2并且资源类型是`CBV`的话，那么其对应的映射就是`register(b2)`了。
    ```hlsl
    cbuffer buffer : register(b2) {...};
    ```
- `RegisterSpace`: 完全和描述符表的一样。

相比描述符表，直接使用描述符的话就相对来说比较简单，我们可以直接在使用的时候设置就好了。

```C++
void SetGraphicsRootConstantBufferView(
    UINT RootParameterIndex,
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation);
```

直接使用指令列表的这个成员函数设置就好了，第一个参数是你要设置的那个描述符是来源标记中的哪个参数，第二个参数是资源的虚拟地址。

### 7.6.4 Root Constants

```C++
struct D3D12_ROOT_CONSTANTS
{
    UINT ShaderRegister;
    UINT RegisterSpace;
    UINT Num32BitValues;
};
```

- `ShaderRegister`: 和描述符一样的参数。
- `RegisterSpace`: 同上。
- `Num32BitValues`: 你将要设置的值个数。

```C++
    D3D12_ROOT_CONSTANTS constant;
    constant.ShaderRegister = 0;
    constant.RegisterSpace = 0;
    constant.Num32BitValues = 3;

    ///Create root signatures
    ...

    float firstData;
    float srcData[9];

    commandList->SetGraphicsRoot32BitConstants(0, 1,
        &firstData, 0);
    commandList->SetGraphicsRoot32BitConstants(0, 9,
        srcData, 1);
```

>对应着色器代码

```hlsl
cbuffer Data : register(b0)
{
    //这里面不能用数组....WTF

    float firstData;

    float srcData0;
    float srcData1;
    float srcData2;
    float srcData3;
    float srcData4;
    float srcData5;
    float srcData6;
    float srcData7;
    float srcData8;
};
```

```C++
void SetGraphicsRoot32BitConstants(
    UINT RootParameterIndex,
    UINT Num32BitValuesToSet,
    const void *pSrcData,
    UINT DestOffsetIn32BitValues);
```

- `RootParameterIndex`: 要设置到哪个来源参数。
- `Num32BitValuesToSet`: 你要设置的值的个数。
- `pSrcData`: 设置的值的第一个元素的地址。
- `DestOffsetIn32BitValues`: 从缓冲中的第几个元素后开始设置。例如例子中第二次设置就是从`srcData0`开始依次填充的，因为它是第二个元素，所以我们要设置为1，表示从第一个元素后开始填充。

并且和描述符一样，我们设置常量的话也是不需要使用描述符堆的。

### 7.6.5 A More Complicated Root Signature Example

### 7.6.6 Root Parameter Versioning

在每次执行绘制指令的时候，我们将会使用当前被设置到着色器的资源。
来源参数只是规定了使用的资源的一些要求，并没有指定具体的资源数据，因此我们通常会在绘制前设置具体的资源到着色器。
并且，对于每次绘制指令，硬件会保留一个快照来记录对于这个绘制指令他使用的状态。
换句话说就是将其版本化(这里对为什么要这样做只有一个猜测，没有办法确保，具体参见Issue5)。
**版本化记录的是具体我们使用了哪些描述符，哪些描述符表等，而不是具体的资源数据** 

假设我们在来源标记中声明了一个资源，但是这并不意味着我们必须要在着色器中使用它。
例如我们在来源标记中声明了第二个来源参数是一个`CBV`，但是我们的着色器代码并没有使用到这个常缓冲，这样并不会报错。
但是如果你在着色器中使用了一个参数，而没有在来源标记中声明的话，肯定会报错(会在创建渲染管线状态的时候报错，被坑过好几次了)。

由于性能原因，我们需要保持我们的来源标记尽可能的小。
至于为什么，硬件会自动版本化就是其中一个原因。
如果你的来源标记越大，那么版本化的时候的快照就越大。
并且也建议你尽可能的不要切换来源标记，因此让多个渲染管线状态使用同样的来源标记的话就可以尽量减少切换了。
主要来说就是我们创建一个较大的来源标记，能够兼容我们的不同的渲染管线状态使用的着色器，也就是说可能我们要使用的着色器未必会全部使用到我们在来源标记声明的资源，但是不同的着色器需要的资源可能不同。因此创建一个能够兼容所有着色器的来源标记的话就不需要切换来源标记了。当然你需要注意的是，如果这个来源标记太大了，可能我们得到的性能减损还不如由于太大导致的性能消耗多，从而导致根本没有得到优化。

## 7.8 SUMMARY

- 在每一帧中等待`GPU`执行完所有的指令后再去进入下一帧的处理是非常低效的，因为这可能会出现`GPU`或者`CPU`处于空闲状态等待另外一个处理器完成它的任务。因此我们就构建了一个叫做`Frame Resources`的技术。通过一个存储每一帧`CPU`要修改的资源的循环数组，我们可以让`CPU`在完成它的任务后不需要等待`GPU`处理完所有任务就进入下一帧的处理。即继续处理下一帧需要修改的资源。当然，如果你的`GPU`不给力或者你的`CPU`太给力，那么`CPU`就会超出`GPU`太多任务，那么我们就还是需要让`CPU`等待`GPU`赶上，但是这样正是我们需要的，因为这代表着我们的`GPU`可以一直工作，虽然我们的`CPU`仍然会有空闲的状态。因此我们还可以考虑在`CPU`空闲的时候来处理一些其他东西，例如AI，物理效果以及游戏逻辑。

- 我们可以通过`ID3D12DescriptorHeap::GetCPUDescriptorHandleForHeapStart`来获取堆中第一个元素的地址。然后我们还可以通过`ID3D12Device::GetDescriptorHandleIncrementSize(DescriptorHeapType type)`来获取堆中每个描述符的大小，从而可以对第一个元素的地址进行偏移获取堆中第任意个元素的地址。

- 来源标记定义了我们在绘制之前要绑定到渲染管线的资源，以及如何将资源映射到着色器中的寄存器中。当我们创建渲染管线状态的时候，我们将会将来源标记和着色器代码进行验证和匹配，如果两者的内容不相符的话，那么就会出现错误。一个来源标记其实就是一组来源参数，来源参数可以是描述符表，描述符或者常量。描述符表是描述符堆中的某个范围内的描述符，一个描述符的话也可以直接绑定到来源标记(并且不需要要求他在堆中)，而常量的话就是直接绑定一个具体的值到来源标记。由于性能的缘故，一个来源标记的大小不能超过`64DWORD`，而一个描述符的开销是`1DWORD`，描述符的话就是`2DWORD`,常量也是`1DWORD`。在每次绘制的时候，硬件都会自动保存一份快照来记录我们用了什么资源，因此我们最好能够尽可能的减小来源标记的大小，从而减少要复制的大小。

- 动态的顶点缓冲主要是用于需要在运行时更新缓冲中的内容这样的情况。我们每次更新缓冲都需要重新将内存里面的数据提交到显存中去，因此是有一定的开销的。