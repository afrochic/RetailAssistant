from pathlib import Path
import os, sys
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
# A private kernelspec ensures execution uses the active environment, not system Python.
kernel_dir=ROOT/'artifacts/jupyter/kernels/retailassist'
kernel_dir.mkdir(parents=True,exist_ok=True)
import json
(kernel_dir/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'RetailAssist','language':'python'}))
os.environ['JUPYTER_PATH']=str(ROOT/'artifacts/jupyter')
os.environ['IPYTHONDIR']=str(ROOT/'artifacts/ipython')
os.environ['MPLCONFIGDIR']=str(ROOT/'artifacts/matplotlib')
p=ROOT/'notebooks/RetailAssist_walkthrough.ipynb'
nb=nbformat.read(p,as_version=4)
NotebookClient(nb,timeout=1200,kernel_name='retailassist',resources={'metadata':{'path':str(ROOT)}},allow_errors=False).execute()
nbformat.write(nb,p)
print('Notebook executed successfully')
