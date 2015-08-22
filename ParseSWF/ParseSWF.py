import os,sys,time,struct,zlib,pylzma
from xml.dom import minidom


def reverseBits(x, n):
    result = 0
    for i in xrange(n):
        if (x >> i) & 1: result |= 1 << (n - 1 - i)
    return result

def ParseTag(Code,Length,Data):
    if Length != len(Data):
        return -1
    if Code == 69:
        if Length != 4:
            return -1
        Flags = struct.unpack("L",Data)[0]
        print "Flags: " + str(hex(Flags))
        #Here parse the flags
        cFlags = ord(chr(Flags))
        print cFlags
    elif Code == 77:
        print "Writing metadata XML"
        DataX = Data.rstrip("\x00").lstrip("\x00")
        fOut = open("xml.xml","w")
        fOut.write(DataX)
        fOut.close()
        xmlX = minidom.parseString(DataX)
        listX = xmlX.getElementsByTagName("dc:format")
        if len(listX)!=0:
            for liX in listX:
                Format = ""
                try:
                    Format = liX.childNodes[0].nodeValue
                except:
                    Format = "N/A"
                print "Format: " + Format
        listX = xmlX.getElementsByTagName("dc:title")
        if len(listX)!=0:
            for liX in listX:
                Title = ""
                try:
                    Title = liX.childNodes[0].nodeValue
                except:
                    Title = "N/A"
                print "Title: " + Title
        listX = xmlX.getElementsByTagName("dc:description")
        if len(listX)!=0:
            for liX in listX:
                Description = ""
                try:
                    Description = liX.childNodes[0].nodeValue
                except:
                    Description = "N/A"
                print "Description: " + Description
        listX = xmlX.getElementsByTagName("dc:publisher")
        if len(listX)!=0:
            for liX in listX:
                Publisher = ""
                try:
                    Publisher = liX.childNodes[0].nodeValue
                except:
                    Publisher = "N/A"
                print "Publisher: " + Publisher
        listX = xmlX.getElementsByTagName("dc:creator")
        if len(listX)!=0:
            for liX in listX:
                Creator = ""
                try:
                    Creator = liX.childNodes[0].nodeValue
                except:
                    Creator = "N/A"
                print "Creator: " + Creator
        listX = xmlX.getElementsByTagName("dc:contributor")
        if len(listX)!=0:
            for liX in listX:
                Contributor = ""
                try:
                    Contributor = liX.childNodes[0].nodeValue
                except:
                    Contributor = "N/A"
                print "Contributor: " + Contributor
        listX = xmlX.getElementsByTagName("dc:language")
        if len(listX)!=0:
            for liX in listX:
                Language = ""
                try:
                    Language = liX.childNodes[0].nodeValue
                except:
                    Language = "N/A"
                print "Language: " + Language
        listX = xmlX.getElementsByTagName("dc:date")
        if len(listX)!=0:
            for liX in listX:
                Date = ""
                try:
                    Date = liX.childNodes[0].nodeValue
                except:
                    Date = "N/A"
                print "Date: " + Date
    return 0

deCompressX = False
NumArgs = len(sys.argv)
inF = ""

if NumArgs < 2:
    print "Usage: DecompressSWF.py input_file_here\r\n"
    print "Usage: DecompressSWF.py -d input_file_here (Dump decompressed file)\r\n"
    sys.exit(-1)

ccc = 0
while ccc < NumArgs:
    if sys.argv[ccc] == "-d" or sys.argv[ccc] == "-D":
        deCompressX = True
        break
    ccc = ccc + 1


inF = sys.argv[1]
if ccc + 1 < NumArgs:
    inF = sys.argv[ccc + 1]

print inF


if os.path.exists(inF)==False or os.path.getsize(inF)==0:
    print "File does not exist or empty\r\n"
    sys.exit(-1)

inFLen = os.path.getsize(inF)

fIn = open(inF,"rb")
fCon = fIn.read()
fIn.close()


Magic = "FWS" #Assume uncompressed
Version = 0
Size = 0
CompressType = 0 #0 ==> Uncompressed
                 #1 ==> Zlib
                 #2 ==> LZMA

Magic = fCon[0:3]
print "Magic: " + Magic

if Magic == "FWS":
    print "Compression Type: None"
    Version = ord(fCon[3])
    szSize = fCon[4:8]
    Size = (struct.unpack("L",szSize))[0]
elif Magic == "CWS":
    print "Compression Type: ZLib"
    CompressType = 1
    Version = ord(fCon[3])
    szSize = fCon[4:8]
    Size = (struct.unpack("L",szSize))[0]
    Conf = fCon[8:10]
    if Conf != "\x78\x01" and Conf != "\x78\x9C" and Conf != "\x78\xDA":
        print "Couldn't find any ZLib structure"
elif Magic == "ZWS":
    print "Compression Type: LZMA"
    CompressType = 2
    Version = ord(fCon[3])
    szSize = fCon[4:8]
    Size = (struct.unpack("L",szSize))[0]
    
    
print "Flash version: " + str(Version)
print "Size: " + str(Size)
NewData = fCon #Assume uncompressed


if CompressType == 1:
    CompCon = fCon[8:]
    decompressed = zlib.decompress(CompCon)
    len_decompressed = len(decompressed)
    if len_decompressed + 8 == Size:
        print "Decompressed successfully"
        NewData = "FWS"
        NewData += fCon[3]
        NewData += fCon[4:8]
        NewData += decompressed
        if deCompressX == True:
            fOutCWS = open("decompressed_zlib.swf","wb")
            fOutCWS.write(NewData)
            fOutCWS.close()
            print "Dumped to decompressed_zlib.swf"
elif CompressType == 2:
    lzma_size = struct.unpack("L",fCon[8:12])[0]
    Props = fCon[12:17] #5-byte properties
    CompCon = fCon[17:] #compressed data
    if len(CompCon) != lzma_size:
        print "Anomaly: LZMA Header does not contain th right size or input File has some appended data"
    decompressed = pylzma.decompress(Props + CompCon)
    len_decompressed = len(decompressed)
    if len_decompressed + 8 == Size:
        print "Decompressed successfully"
        NewData = "FWS"
        NewData += fCon[3]
        NewData += fCon[4:8]
        NewData += decompressed
        if deCompressX == True:
            fOutZWS = open("decompressed_lzma.swf","wb")
            fOutZWS.write(NewData)
            fOutZWS.close()
            print "Dumped to decompressed_lzma.swf"
        

nBits = ord(NewData[8])>>3
print "nBits: " + str(nBits)
szRect = (5 + (nBits*4))
while szRect % 8 != 0:
    szRect += 1
szRect = szRect / 8
print "Size of RECT structure: " + str(szRect)
OffFrameRate = 8 + szRect
FrameRateLittle = NewData[OffFrameRate:OffFrameRate+2]
FrameRateBig = FrameRateLittle[1] + FrameRateLittle[0]
FrameRate = struct.unpack("H",FrameRateBig)[0]
print "Frame Rate: " + str(FrameRate)

OffFrameCount = OffFrameRate + 2
FrameCount = struct.unpack("H",NewData[OffFrameCount:OffFrameCount+2])[0]
print "Frame Count: " + str(FrameCount)

TagOffset = OffFrameCount + 2
#Start tag processing here
NumTags = 0
iAnomaly = 0
HasMetadata = False
AS3 = False
NoCrossDomainCache = False
UseNetwork = False
TagIDs = []
while TagOffset < Size:
    Curr = TagOffset
    TagCodeAndLength = struct.unpack("H",NewData[Curr:Curr+2])[0]
    print hex(TagCodeAndLength)
    TagCode = TagCodeAndLength >> 6    #& 0x3FF
    print "Tag Code: " + str(hex(TagCode)) + " (" + str(TagCode) + ")"
    
    #First tag must be the File Attributes tag
    if NumTags == 0 and TagCode != 69: 
        print "Anomaly " + str(iAnomaly) + ": first tag is not FileAttributes"
        iAnomaly = iAnomaly + 1
    #Check for duplicate tags
    if len(TagIDs) != 0:
        NumT = len(TagIDs)
        Ru = 0
        while Ru < NumT:
            if TagIDs[Ru]==TagCode:
                print "Anomaly " + str(iAnomaly) + ": duplicate tags of code " + str(TagCode)
                iAnomaly = iAnomaly + 1
            Ru = Ru + 1
    #If MetaData tag exists, then FileAttributes.HasMetadata must be set
    if TagCode == 77:
        if HasMetadata == False:
            print "Anomaly: Metadata exists without HasMetadata file attribute"
            iAnomaly = iAnomaly + 1
            
    TagIDs.append(TagCode)
    Length = TagCodeAndLength & 0x3F
    print "Tag Length: " + str(hex(Length))
    Curr = Curr + 2
    TagData = ""
    Long = False
    if Length >= 0x3F:  #Long of length is 63, ignore this length and parse the next DWORD for real length
        print "Long Tag"
        Length = struct.unpack("L",NewData[Curr:Curr+4])[0]
        print "Real Length: " + str(Length)
        Curr = Curr + 4
        Long = True
    else:
        print "Short Tag"
    TagData = NewData[Curr:Curr+Length]
    print len(TagData)
    Curr = Curr + Length
    TagOffset = Curr
    NumTags += 1
    if TagCode == 69:
        if len(TagData)!=4:
            print "Anomaly: Length of FileAttributes tag is not 4"
            iAnomaly = iAnomaly + 1
        else:
            xFlags = struct.unpack("L",TagData)[0]
            print "File attributes: " + str(hex(xFlags))
            if xFlags > 255:
                print "Anomaly: unused FileAttributes bits are set"
                iAnomaly = iAnomaly + 1
            cFlags = ord(chr(xFlags))
            cFlags_r = reverseBits(cFlags,8)
            print cFlags_r
            if cFlags_r & 0x7:
                print "Anomaly: reversed FileAttributes bits are used"
                iAnomaly = iAnomaly + 1
            if cFlags_r & 0x8:
                HasMetadata = True
                print "HasMetadata: True"
            else:
                print "HasMetadata: False"
            if cFlags_r & 16:
                AS3 = True
                print "ActionScript3: True"
            else:
                print "ActionScript3: False"
            if cFlags_r & 32:
                NoCrossDomainCache = True
                print "NoCrossDomainCache: True"
            else:
                print "NoCrossDomainCache: False"
            if cFlags_r & 64:
                print "Anomaly: reversed FileAttributes bit is used"
                iAnomaly = iAnomaly + 1
            if cFlags_r & 128:
                UseNetwork = True
                print "UseNetwork: True"
            else:
                print "UseNetwork: False"
                
    else:
        ret = ParseTag(TagCode,Length,TagData)
        if ret == -1:
            print "Error parsing tag"
    print "---------------------------------"
print "Number of Tags: " + str(NumTags)






