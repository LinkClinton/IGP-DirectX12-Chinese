import markdown2

buildList = open("./Build/buildList.txt", "r")

allFile = buildList.readlines()

head = open("./Build/head.html","r")

headHtml = head.read()

for item in allFile:
    fileName = item.rstrip('\n')
    html = headHtml
    html += markdown2.markdown_path(fileName + ".md", 
        extras=["fenced-code-blocks","code-friendly", "code-color", "tables"])
    output = open("./Build/"+fileName+".html","w",encoding= "utf-16")
    output.write(html)
    pass
    