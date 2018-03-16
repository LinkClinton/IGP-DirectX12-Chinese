import markdown2

def getMathCode(str):
    isBegin = False
    isDouble = False
    
    mathCode = ""

    result = []

    for i in range(0, len(str)):
        isCurrentEnd = False

        if (str[i] is '$'):
            if (isBegin is False):
                isBegin = True
                isDouble = False
            else:
                if (isDouble is False):
                    if (str[i-1] is '$'):
                        isDouble = True
                    else:
                        isBegin = False
                        isDouble = False
                        isCurrentEnd = True
                else:
                    if (str[i-1] is '$'):
                        isBegin = False
                        isDouble = False
                        isCurrentEnd = True
        
        if (isBegin is True or isCurrentEnd is True):
            mathCode += str[i]

        if (isCurrentEnd is True):
            result.append(mathCode)
            mathCode = ""

        pass

    return result

htmlHead = open("./head.html").read()
buildFile = open("./buildList.txt").readlines()

for item in buildFile:
    fileName = item.rstrip('\n')
    
    sourceFile = open(fileName + ".md", encoding = "utf-8").read()
    mathCodes = getMathCode(sourceFile)
    mathCodeCount = 0
    
    result = htmlHead
    
    html = markdown2.markdown_path(fileName + ".md", 
        extras=["fenced-code-blocks","code-friendly", "code-color", "tables"])

    isBegin = False
    isDouble = False

    for i in range(0, len(html)):
        isCurrentEnd = False

        if (html[i] is '$'):
            if (isBegin is False):
                isBegin = True
                isDouble = False
            else:
                if (isDouble is False):
                    if (html[i-1] is '$'):
                        isDouble = True
                    else:
                        isBegin = False
                        isDouble = False
                        isCurrentEnd = True
                else:
                    if (html[i-1] is '$'):
                        isBegin = False
                        isDouble = False
                        isCurrentEnd = True
        
        if (isBegin is False and isCurrentEnd is False):
            result += html[i]

        if (isCurrentEnd is True):
            result += mathCodes[mathCodeCount]
            mathCodeCount += 1

    pass

    output = open("./" + fileName + ".html", "w" , encoding= "utf-16")
    output.write(result)

pass

indexHtml = htmlHead + markdown2.markdown_path("readme.md", 
    extras=["fenced-code-blocks","code-friendly", "code-color", "tables"])

output = open("./"+"index.html","w",encoding= "utf-16")
output.write(indexHtml)

