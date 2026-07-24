python build.py build_ext --inplace

@DEL /Q LZSS.pyd
@REN LZSS.cp310-win_amd64.pyd LZSS.pyd

@DEL /Q ROBOT.pyd
@REN ROBOT.cp310-win_amd64.pyd ROBOT.pyd
@DEL /Q SNMSG.pyd
@REN SNMSG.cp310-win_amd64.pyd SNMSG.pyd
@DEL /Q SNDATA.pyd
@REN SNDATA.cp310-win_amd64.pyd SNDATA.pyd
@DEL /Q SCRIPT.pyd
@REN SCRIPT.cp310-win_amd64.pyd SCRIPT.pyd

@RMDIR /S /Q build
