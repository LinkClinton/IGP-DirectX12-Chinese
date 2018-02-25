# 关于翻译的格式

## 翻译环境

- Visual Studio Code + Markdown Math + markdownlint.

后面两个是插件。文本编码是UTF-8。尾行序列CRLF

## 翻译格式

- 关于标题，按照原文为准，全部大写并且注意在标题名前面加上数字表示第几章第几节等。
- 关于一些专有名词或者英文单词最好使用``符号包括起来，以突出显示和区分。
- 关于专有名词的翻译，有比较准确的翻译的使用中文然后用括号加**来突出原文，如果没有中文翻译的就使用原文(注意加星号加粗)。
- 关于示例代码，建议以较为随意的C++代码加上英文来写，而不是复杂的代码。代码部分请使用`代码块`来包含，下面是例子。

    ```C++
        string start = "Hello, World!";
    ```

- 关于图片，个人是截图PDF中的内容，这个只要你能够提取出图片即可。图片下面通常会有解释说明，这部分也请截图，自己判断是否需要起一个段落来翻译图片下面的解释说明。图片引用格式。关于图片文件名，主要是参见原文中的编号。

![Image](Images/4.1.png)

- 关于出现的结构类型(struct)介绍，保持格式以及使用代码块括起来，必要的可以翻译每个成员的作用。
    ```C++
    struct DXGI_MODE_DESC
    {
        UINT Width; //缓存的宽度
        UINT Height; //缓存的高度
        DXGI_RATIONAL RefreshRate;
        DXGI_FORMAT Format; //缓存的格式
        DXGI_MODE_SCANLINE_ORDER ScanlineOrdering;
        DXGI_MODE_SCALING Scaling; //如何在显示器上缩放显示
    };
    ```

- 关于函数参数或者结构体成员的作用的翻译，例子如下。

> - `BufferDesc`: 描述我们创建的`BackBuffer`的属性，主要属性就是他的宽度高度以及他的格式。其余的可以去参考**SDK**文档。
> - `SampleDesc`: 多重采样的数量和质量等级，我们设置成采样数量为1，质量等级为0。
> - `BufferUsage`: 设置为`DXGI_USAGE_RENDER_TARGET_OUTPUT`。
> - `BufferCount`: 我们在交换链中要使用多少个缓冲，由于我们使用双缓冲因此设置为2。
> - `OutputWindow`: 我们要呈现的窗口的句柄。
> - `Windowed`: 设置为`true`就是窗口模式，否则是全屏模式。
> - `SwapEffect`: 设置为`DXGI_SWAP_EFFECT_FLIP_DISCARD`。
> - `Flags`: 一些其他设置。如果你设置了`DXGI_SWAP_CHAIN_FLAG_ALLOW_MODE_SWITCH`，那么在你切换到全屏模式的时候就会选择一个最适合当前程序的显示模式，如果你没有设置这个属性，那么你切换成全屏的时候他就使用当前桌面的显示模式。

- 关于所有的数学公式或者一些数值请使用latex。

应该就这些吧吧吧吧。

## 建议翻译的时候一边预览一边写。

