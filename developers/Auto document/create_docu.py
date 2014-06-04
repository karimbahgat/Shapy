import sys
sys.path.append(r"C:\Users\BIGKIMO\Github\GitDoc")
import gitdoc

FILENAME = "shapy"
FOLDERPATH = r"C:\Users\BIGKIMO\Github\Shapy"
OUTPATH = r"C:\Users\BIGKIMO\Github\Shapy"
OUTNAME = "README"
EXCLUDETYPES = ["variable","module"]
gitdoc.DocumentModule(FOLDERPATH,
                  filename=FILENAME,
                  outputfolder=OUTPATH,
                  outputname=OUTNAME,
                  excludetypes=EXCLUDETYPES,
                  )
