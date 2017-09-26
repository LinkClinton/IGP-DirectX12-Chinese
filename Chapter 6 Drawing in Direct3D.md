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

我们虽然定义了顶点格式，但是我们同样需要告诉`Direct3D`我们的顶点格式，不然的话`Direct3D`是没法知道我们给顶点附加了哪些额外的数据。
我们使用`D3D12_INPUT_LAYOUT_DESC`来做这件事。

```C++

struct D3D12_INPUT_LAYOUT_DESC 
{
    const D3D12_INPUT_ELEMENT_DESC *pInputElementDescs;
    UINT NumElements;
};

```

- `pInputElementDescs`: 一个数组，告诉`Direct3D`我们的顶点附加的数据信息。
- `NumElements`: 数组的大小。

`pInputElementDescs`里面的每一个元素都相当于顶点格式的一个附加数据信息。
因此如果我们的一个顶点格式他有两个附加数据信息的话，那么这个数组的大小就需要是两个。

```C++
struct D3D12_INPUT_ELEMENT_DESC
{
    LPCSTR SemanticName;
    UINT SemanticIndex;
    DXGI_FORMAT Format;
    UINT InputSlot;
    UINT AlignedByteOffset;
    D3D12_INPUT_CLASSIFICATION InputSlotClass;
    UINT InstanceDataStepRate;
};
```

- `SemanticName`: 一个用于联系元素的字符串。他的值必须在合法的范围内。我们使用这个来将顶点中的元素映射到着色器的输入数据中去。参见图片[6.1](#Image6.1)。
<img src="Images/6.1.png" id = "Image6.1"> </img>
- `SemanticIndex`: 索引值，具体可以参见图片[6.1](#Image6.1)。例如一个顶点可能会有不止一个纹理坐标，我们必须区分这些纹理坐标，因此我们就加入了索引值来区分一个顶点里面的多个纹理坐标。如果一个`semanticName`没有加上索引的话就默认为索引值为0。例如`POSITION`就是`POSITION0`。
- `Format`: 附加的数据信息的格式，类型是`DXGI_FORMAT`。
- `InputSlot`: 指定这个元素从哪个输入口进入，`Direct3D`支持16个输入口(0-15)输入顶点数据。对于现在来说，我们只使用0输入口。
- `AlignedByteOffset`: 内存偏移量，单位是字节。从顶点结构的开端到这个元素的开端的字节大小。下面是一个例子。
    ```C++
    struct Vertex
    {
        Float3 Pos; // 0-byte offset
        Float3 Normal; // 12-byte offset
        Float2 Tex0; // 24-byte offset
        Float2 Tex1; // 32-byte offset
    };
    ```
- `InputSlotClass`: 现在默认使用`D3D12_INPUT_PER_VERTEX_DATA`。另外的一个类型是用于`Instancing`技术的。

这里我们给一个例子: 

```C++
struct Vertex
{
    Float3 Pos; // 0-byte offset
    Float3 Normal; // 12-byte offset
    Float2 Tex0; // 24-byte offset
    Float2 Tex1; // 32-byte offset
};

D3D12_INPUT_ELEMENT_DESC desc [] = 
{
    	{“POSITION”, 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0,  D3D12_INPUT_PER_VERTEX_DATA, 0},
        {“NORMAL”,   0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 12, D3D12_INPUT_PER_VERTEX_DATA, 0},
        {“TEXCOORD”, 0, DXGI_FORMAT_R32G32_FLOAT,    0, 24, D3D12_INPUT_PER_VERTEX_DATA, 0},
        {“TEXCOORD”, 1, DXGI_FORMAT_R32G32_FLOAT,    0, 32, D3D12_INPUT_PER_VERTEX_DATA, 0}     
};
```
 
 ## <element id = "6.2"> 6.2 VERTEX BUFFERS </element>

 为了能够让`GPU`访问一组顶点的数据信息，我们需要将顶点信息放入到`GPU`资源中去(**ID3D12Resource**)，我们称之为缓冲。
 我们将存储顶点数据的缓冲称之为顶点缓冲(`Vertex Buffer`)。
 缓冲比纹理简单一些，他只有一维，并且他没有纹理明细(`MipMaps`)，过滤器(`filters`)，多重采样(`multisampling`)这些东西。
 无论在什么时候，如果我们要给`GPU`提供一组数据信息例如顶点数据信息，我们都会使用缓冲来实现。

 我们在之前讲过通过填充`D3D12_RESOURCE_DESC`类型来创建一个`ID3D12Resource`。
 因此我们也会通过这样的方式来创建一个缓冲，即填充`D3D12_RESOURCE_DESC`结构来描述我们要创建的缓冲的属性，然后使用`ID3D12Device::CreateCommittedResource`创建缓冲。

 在`d3dx12.h`中提供了一个简便的类型`CD3D12_RESOURCE_DESC`来创建资源，具体可以去参见`d3dx12.h`。

 **注意我们在`Direct3D 12`中并没有定义一个具体的类型来表示这个资源是一个缓冲或者是一个纹理(`Direct3D 11`中是这样做的)。
 因此我们在创建资源的时候需要通过`	D3D12_RESOURCE_DESC::D3D12_RESOURCE_DIMENSION`来指定资源的类型。**

 对于静态的图形(即每一帧中通常不会改变)，我们会将他的顶点缓冲放在默认堆中(**Default Heap**)以保持最优的性能，通常大部分游戏中的图形都会放在默认堆中，例如树，建筑，地形，人物等。
 因为我们在创建好它的顶点缓冲后，`GPU`只会读取里面的顶点信息来绘制它，而不会做其他的事情，因此将其放在默认堆里面是最好的。
 然而由于`GPU`并不能将数据写入到处于默认堆里面的资源，我们该如何将初始的顶点数据放到缓冲中去？

 为了实现这个，我们需要创建一个上传缓冲资源(`Upload Buffer`)，它会被放在上传堆中(**Upload Heap**)。
 回顾4.3.8章节，当我们要将数据从内存拷贝到显存中去的时候，我们提交了一个资源到上传堆中。
 在我们创建完一个上传缓冲后，我们将顶点数据拷贝到上传缓冲中，然后我们从上传缓冲中拷贝顶点数据到我们的顶点缓冲中去。

 之后的内容是一个例子，这里可以自己去看代码。我只将几个主要使用的结构体类型介绍下。

 ```C++
 struct D3D12_SUBRESOURCE_DATA
 {
    const void *pData;
    LONG_PTR RowPitch;
    LONG_PTR SlicePitch;
 };
 ```

 - `pData`: 数组的首元素指针。
 - `RowPitch`: 对于缓冲来说他就是我们拷贝的数据的大小，单位字节。
 - `SlicePitch`: 对于缓冲来说他就是我们拷贝的数据的大小，单位字节。

注意的是，对于顶点缓冲来说，我们创建他的描述符是不需要将其放入描述符堆中的。

```C++
struct D3D12_VERTEX_BUFFER_VIEW
{
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation;
    UINT SizeInBytes;
    UINT StrideInBytes;
};
```

- `BufferLocation`: 我们想要使用的顶点缓冲的虚拟地址。我们可以使用`ID3D12Resource::GetGPUVirtualAddress`来获取地址。
- `SizeInBytes`: 描述符可以只声明他只使用缓冲中的一部分数据，这个参数就是用来告诉我们要使用的缓冲大小，单位字节，从`BufferLocation`位置开始往后偏移。
- `StrideInBytes`: 每个顶点元素的大小，单位字节。

在我们创建完缓冲和缓冲的描述符后，我们可以将他们绑定到渲染管道的输入口，然后在输入装配阶段将顶点缓冲输入进去。


```C++
    void ID3D12GraphicsCommandList::IASetVertexBuffers(
        UINT StartSlot,
        UINT NumBuffers,
        const D3D12_VERTEX_BUFFER_VIEW *pViews);
```

- `StartSlot`: 绑定的顶点缓冲的输入口的起始位置，总共有16个，范围在0-15之间。
- `NumBuffers`: 我们要绑定的顶点缓冲的个数，我们假设我们绑定n个顶点缓冲，输入口的起始位置是k，那么第i个顶点缓冲的输入口就是`k + i - 1`。
- `pViews`: 我们要绑定的顶点缓冲的描述符数组的首元素的地址。

**官网中说的是DX12最大支持的输入口个数是32。**

由于要支持多个顶点缓冲从任意一个输入口输入数据，这个函数设计的就有点复杂了。
但是在这里我们只使用一个输入口。在章节最后的练习中我们会使用到两个输入口。

只有当我们改变这个输入口绑定的顶点缓冲的时候，原本的顶点缓冲才会取消绑定。
因此我们虽然只使用一个输入口但是我们仍然可以使用多个顶点缓冲。例如这样。

```C++
    D3D12_VERTEX_BUFFER_VIEW_DESC BufferView1;
    D3D12_VERTEX_BUFFER_VIEW_DESC BufferView2;

    /*Create Vertex Buffer Views*/

    commandList->IASetVertexBuffers(0, 1, &BufferView1);

    /*Draw by using VertexBuffer1*/

    commandList->IASetVertexBuffers(0, 1, &BufferView2);

    /*Draw by using VertexBuffer2*/
```

绑定一个顶点缓冲到输入口并不代表我们绘制了这个缓冲，我们只是准备好让顶点输入到渲染管道中而已。
因此最后我们还需要使用绘制函数来绘制这些顶点。

```C++
    void ID3D12CommandList::DrawInstanced(
        UINT VertexCountPerInstance,
        UINT InstanceCount,
        UINT StartVertexLocation,
        UINT StartInstanceLocation);
```

- `VertexCountPerInstance`: 我们需要绘制的顶点个数(对于每个实例来说)。
- `InstanceCount`: 我们要绘制的实例个数，这里我们设置为1。
- `StartVertexLocation`: 指定从顶点缓冲中的第几个顶点开始绘制。
- `StartInstanceLocation`: 这里我们设置为0。

`VertexCountPerInstance`和`StartVertexLocation`一起决定了我们要绘制顶点缓冲中的哪个范围。
图片[6.2](#Image6.2)给出了例子。

<img src="Images/6.2.png" id = "Image6.2"> </img>

`StartVertexLocation`指定了我们要绘制第一个顶点在顶点缓冲中的位置，`VertexCountPerInstance`指定了我们要绘制的顶点个数。

`DrawInstanced`并没有让我们指定我们绘制的时候使用的图元的类型。
因此我们需要使用`ID3D12GraphicsCommandList::IASetPrimitiveTopology`去设置。

## <element id = "6.3"> 6.3 INDICES AND INDEX BUFFERS</element>

和顶点类似，为了能够让`GPU`能够访问到索引数据，我们同样需要将索引数据放到缓冲中去。
我们称之为索引缓冲。索引缓冲的创建方式和顶点缓冲是一样的，因此这里就不再讨论了。

我们同样需要将索引缓冲绑定到渲染管道中去，因此我们也要为索引缓冲创建描述符，并且和顶点缓冲一样，我们不需要使用到描述符堆。

```C++
struct D3D12_INDEX_BUFFER_VIEW
{
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation;
    UINT SizeInBytes;
    DXGI_FORMAT Format; 
};
```

- `BufferLocation`: 和顶点缓冲的一样。
- `SizeInBytes`: 和顶点缓冲的一样。
- `Format`: 一个索引占据的字节大小，必须设置为`DXGI_FORMAT_R16_UINT`或者`DXGI_FORMAT_R32_UINT`。

和顶点缓冲一样，以及其他的`Direct3D`资源我们如果想要使用他们的话，一般都需要将其绑定到渲染管道中去。
这里我们同样也需要将索引缓冲绑定到和顶点缓冲一样的阶段(使用`ID3D12CommandList::SetIndexBuffer`)，即输入装配阶段。


下面的代码是一个例子，你可以去自己看看。

如果你需要使用索引缓冲的话，我们就不能够使用`DrawInstanced`来绘制图形了，而必须使用`DrawIndexedInstanced`来绘制。

```C++
    ID3D12GraphicsCommandList::DrawIndexedInstanced(
        UINT IndexCountPerInstance,
        UINT InstanceCount,
        UINT StartIndexLocation,
        INT BaseVertexLocation,
        UINT StartInstanceLocation);
```

- `IndexCountPerInstance`: 我们绘制的时候使用的索引个数。
- `InstanceCount`: 实例个数，这里我们设置为1。
- `StartIndexLocation`: 指定从顶点缓冲中的哪个索引位置开始绘制。
- `BaseVertexLocation`: 指定我们绘制的时候使用的第一个顶点在顶点缓冲中的位置，即在顶点缓冲中这个顶点之前的顶点我们并不使用，我们从这个顶点开始重新编号。
- `StartInstanceLocation`: 我们这里设置为0。


