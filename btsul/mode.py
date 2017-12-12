
def readM(fileName="modes.txt"):
    file=open(fileName,"rb")
    ans=[]
    get = file.read(1)
    while get:
        num=ord(get)
        get=file.read(num)
        ans.append(get)
        get = file.read(1)
    file.close()
    return ans


def writeM(data,fileName="modes.txt"):
    file=open(fileName,"wb")
    data=set(data)
    for m in data:
        c=chr(len(m))
        file.write(c)
        file.write(m)
    file.close()


if __name__=="__main__":
    #ls=["\x6a\x76\x2b\x45\xea"]
    ls=["he","she","her","hers"]
    writeM(ls)