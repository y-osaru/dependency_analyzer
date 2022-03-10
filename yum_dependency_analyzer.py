# coding: UTF-8
import subprocess
import traceback
import re
import sys
from collections import OrderedDict

#上位パッケージですでに依存関係があると分かっている物を保存しておくメモ(下位パッケージで上位と同じパッケージが出てくるパターンが有った。無限ループになるのでメモ化)
memo = []

def analyzeDependency(indentCount,package):
  """
  依存関係を解析する
  """
  printDependencyPackage(indentCount,package)

  #依存関係取得
  dependPackages = getDependencyPackages(package)

  if len(dependPackages) > 0:
    for dependPackage in dependPackages:
      if dependPackage not in memo:
        #メモに追加
        memo.append(dependPackage)
        analyzeDependency(indentCount+1,dependPackage)
      else:
        if isPrintFull:
          printDependencyPackage(indentCount+1,dependPackage+"(already depend)")

def getDependencyPackages(package):
  """
  指定されたパッケージの依存関係を取得
  """
  cmd = "yum deplist " + package
  res = execCmd(cmd)
  
  #依存関係のあるパッケージのリストを取得
  dependPackages = re.findall("provider: (.*)",res.decode("utf-8"))

  #重複削除
  return list(OrderedDict.fromkeys(dependPackages))

def printDependencyPackage(indentCount,package):
  """
  出力
  """
  indentStr = ""
  for i in range(indentCount):
    indentStr += " "
  
  print(indentStr+package)

def execCmd(cmd):
  """
  コマンド実行
  """
  try:
    res = subprocess.check_output(cmd,shell=True,stderr=subprocess.DEVNULL)
    return res
  except Exception as e:
    print("Exec Error cmd:%s" % cmd)
    raise e

isPrintFull = False

def main():
  """
  yumでインストールする際の依存関係を解析するツール
  解析したいパッケージ
   依存パッケージA
    依存パッケージA-1
   依存パッケージB
    依存パッケージB-1
    依存パッケージB-2
     ...
  というような出力を行う。(インデントはスペース)
  yum deplist [パッケージ名]が使える環境であること
  第二引数にfullをつけると、上位ですでに依存すると分かっているパッケージも下位で表示する
  """
  try:
    argv = sys.argv
    package = argv[1]
    if len(argv) >= 3 and "full" == argv[2]:
      global isPrintFull
      isPrintFull = True
      print("*print full*")
    else:
      print("*print summary*")
    
    #依存関係解析
    analyzeDependency(0,package)
  except Exception as e:
    print(e)

if __name__ == '__main__':
  main()

