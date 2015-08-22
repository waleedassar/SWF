import os,sys,time,struct
import zlib,pylzma

NumArgs = len(sys.argv)


if NumArgs != 2 and NumArgs != 3:
    print "Usage: CompressSWF.py Input.swf (ZLib Compression Assumed)"
    print "Usage: CompressSWF.py -zlib Input.swf"
    print "Usage: CompressSWF.py -lzma Input.swf"
    sys.exit(-1)

Compression = 1 #Zlib compression assumed (1 ==> Zlib, 2 ==> LZMA)
inF = sys.argv[1]

for i in range(1,NumArgs):
    t_Arg = sys.argv[i].lower()
    if (t_Arg[0]=="-" or t_Arg[0]=="/") and len(t_Arg) > 1:
        tt_Arg = t_Arg[1:]
        if tt_Arg == "zlib":
            Compression = 1
            if i + 1 < NumArgs:
                inF = sys.argv[i+1]
        if tt_Arg == "lzma":
            Compression = 2
            if i + 1 < NumArgs:
                inF = sys.argv[i+1]


if os.path.exists(inF)==False:
    print "Input file does not exist"
    sys.exit(-2)

inFLen = os.path.getsize(inF)
if inFLen == 0:
    print "Input file is empty"
    sys.exit(-2)

tex = inF + " is being "
if Compression == 1:
    tex += "ZLib-Compressed"
elif Compression == 2:
    tex += "LZMA-Compressed"

print tex + "..."

fIn = open(inF,"rb")
fCon = fIn.read()
fIn.close()

if inFLen <= 8:
    print "Input file is too small"
    sys.exit(-3)

Magic = fCon[0:3]
if Magic != "FWS":
    if Magic == "CWS":
        print "Input file is already compressed (ZLib)"
    elif Magic == "ZWS":
        print "Input file is already compressed (LZMA)"
    else:
        print "Input file is not flash file"

print "Magic: " + Magic

Version = struct.unpack("B",fCon[3])[0]
print "Version: " + str(Version)
Size = struct.unpack("L",fCon[4:8])[0]
if Size != inFLen:
    print "Anomaly: The size field found in SWF header does not match file size"
    if inFLen > Size:
        Diff = inFLen - Size
        print "Anomaly: " + str(Diff) + " bytes are append to end of input file"


NewFile = ""
if Compression == 1:
    NewFile += "CWS"
elif Compression == 2:
    NewFile += "ZWS"

NewFile += fCon[3]

inFLen_pak = struct.pack("L",inFLen)
NewFile += inFLen_pak

if inFLen > 8:
    DecompCon = fCon[8:]
    T = ""
    if Compression == 1:
        T = zlib.compress(DecompCon)
    elif Compression == 2:
        T = pylzma.compress(DecompCon)
        len_T = len(T)
        s_len_T = struct.pack("L",len_T)
        NewFile += s_len_T
    if T != "":
        NewFile += T
        outFileName = ""
        if Compression == 1:
            outFileName = "zlib_compressed.swf"
        elif Compression == 2:
            outFileName = "lzma_compressed.swf"
        fOut = open(outFileName,"wb")
        fOut.write(NewFile)
        fOut.close()
        print "Compressed file was written to " + outFileName
        sys.exit(0)
