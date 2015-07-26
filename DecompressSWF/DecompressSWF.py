import os,sys,time,struct,zlib,pylzma



if len(sys.argv) != 2:
    print "Usage: DecompressSWF.py input_file_here\r\n"
    sys.exit(-1)


inF = sys.argv[1]

if os.path.exists(inF)==False or os.path.getsize(inF)==0:
    print "File does not exist or empty\r\n"
    sys.exit(-1)

inFLen = os.path.getsize(inF)

fIn = open(inF,"rb")
fCon = fIn.read()
fIn.close()


Magic = "FWS"
Version = 0
Size = 0
CompressType = 0 #0 ==> Uncompressed
                 #1 ==> Zlib
                 #2 ==> LZMA

Magic = fCon[0:3]
print "Magic: " + Magic

if Magic == "FWS":
    print "Input file is not compresses"
    Version = ord(fCon[3])
    szSize = fCon[4:8]
    Size = (struct.unpack("L",szSize))[0]
elif Magic == "CWS":
    print "Input file is ZLib-compressed"
    CompressType = 1
    Version = ord(fCon[3])
    szSize = fCon[4:8]
    Size = (struct.unpack("L",szSize))[0]
    Conf = fCon[8:10]
    if Conf != "\x78\x01" and Conf != "\x78\x9C" and Conf != "\x78\xDA":
        print "Couldn't find any ZLib structure"
elif Magic == "ZWS":
    print "Input file is LZMA-compressed"
    CompressType = 2
    Version = ord(fCon[3])
    szSize = fCon[4:8]
    Size = (struct.unpack("L",szSize))[0]
    
    
print "Flash version: " + str(Version)
print "Size: " + str(Size)

if CompressType == 1:
    CompCon = fCon[8:]
    decompressed = zlib.decompress(CompCon)
    len_decompressed = len(decompressed)
    if len_decompressed + 8 == Size:
        print "Decompressed successfully"
        
        
if decompressed != 0 and decompressed != "":
    if CompressType == 1:
        fOut = open("ZlibDecompressed.bin","wb")
        fOut.write("FWS")
        fOut.write(fCon[3])
        fOut.write(fCon[4:8])
        fOut.write(decompressed)
    fOut.close()
