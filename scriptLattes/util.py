#!/usr/bin/env python 
# encoding: utf-8
#
#

import os, shutil, Levenshtein
SEP = os.path.sep
BASE = 'scriptLattes' + SEP
ABSBASE = os.path.abspath('.') + SEP

class OutputStream:
    def __init__(self, output, encoding):
        self.encoding = encoding
        self.output = output
    def write(self, text):
        if self.encoding:
            text = text.decode(self.encoding)
        else:
            try:
                text = text.decode('utf8').encode('iso-8859-1')
            except:
                try:
                    text = text.encode('iso-8859-1')
                except:
                    pass
        try:
            self.output.write(text)
        except:
            try:
                self.output.write(unicode(text))
            except:
                self.output.write('ERRO na impressao')
                
def copiarArquivos(dir):
    base = ABSBASE
    shutil.copy2(base + 'css'+SEP+'scriptLattes.css', dir)
    shutil.copy2(base + 'imagens'+SEP+'lattesPoint0.png', dir)
    shutil.copy2(base + 'imagens'+SEP+'lattesPoint1.png', dir)
    shutil.copy2(base + 'imagens'+SEP+'lattesPoint2.png', dir)
    shutil.copy2(base + 'imagens'+SEP+'lattesPoint3.png', dir)
    shutil.copy2(base + 'imagens'+SEP+'lattesPoint_shadow.png', dir)
    shutil.copy2(base + 'imagens'+SEP+'doi.png', dir)
    print "Arquivos salvos em: >>'%s'<<" % os.path.abspath(dir)

# ---------------------------------------------------------------------------- #
def compararCadeias(str1, str2, qualis=False):
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    if len(str1)==0 or len(str2)==0:
        return 0
    
    if len(str1)>=20 and len(str2)>=20 and (str1 in str2 or str2 in str1):
        return 1

    if qualis:
        dist = Levenshtein.ratio(str1, str2)
        if len(str1)>=10 and len(str2)>=10 and dist>=0.80:
            #return 1
            return dist

    else:
        if len(str1)>=10 and len(str2)>=10 and Levenshtein.distance(str1, str2)<=5:
            return 1
    return 0

def criarDiretorio(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        ### except OSError as exc:
        except:
            print "\n[ERRO] Não foi possível criar ou atualizar o diretório: "+dir.encode('utf8')
            print "[ERRO] Você conta com as permissões de escrita? \n"
            return 0
    return 1