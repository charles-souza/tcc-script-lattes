# coding=utf-8
import os
import sys
import shutil

import Levenshtein


def compararCadeias(str1, str2, qualis=False):
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    if len(str1) == 0 or len(str2) == 0:
        return 0

    if len(str1) >= 20 and len(str2) >= 20 and (str1 in str2 or str2 in str1):
        return 1

    if qualis:
        dist = Levenshtein.ratio(str1, str2)
        if len(str1) >= 10 and len(str2) >= 10 and dist >= 0.80:
            # return 1
            return dist

    else:
        if len(str1) >= 10 and len(str2) >= 10 and Levenshtein.distance(str1, str2) <= 5:
            return 1
    return 0


def criarDiretorio(diretorio):
    if not os.path.exists(diretorio):
        try:
            os.makedirs(diretorio)
        # ## except OSError as exc:
        except:
            print "\n[ERRO] Não foi possível criar ou atualizar o diretório: " + diretorio.encode('utf8')
            print "[ERRO] Você conta com as permissões de escrita? \n"
            return 0
    return 1


def copiarArquivos(diretorio):
    shutil.copy2(sys.path[0] + '/css/scriptLattes.css', diretorio)
    shutil.copy2(sys.path[0] + '/imagens/lattesPoint0.png', diretorio)
    shutil.copy2(sys.path[0] + '/imagens/lattesPoint1.png', diretorio)
    shutil.copy2(sys.path[0] + '/imagens/lattesPoint2.png', diretorio)
    shutil.copy2(sys.path[0] + '/imagens/lattesPoint3.png', diretorio)
    shutil.copy2(sys.path[0] + '/imagens/lattesPoint_shadow.png', diretorio)
    shutil.copy2(sys.path[0] + '/imagens/doi.png', diretorio)
