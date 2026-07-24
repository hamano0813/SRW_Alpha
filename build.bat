@title build project
RMDIR /S /Q dist
python -m venv venv --upgrade-deps
call venv/scripts/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
cd src/structure/destructor/
call build.bat
cd ../../..
pyinstaller project.spec
RMDIR /S /Q build
RMDIR /S /Q venv
start dist
