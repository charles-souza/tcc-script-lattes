#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import urllib2, requests
from BeautifulSoup import BeautifulSoup
import codecs
import pickle
from HTMLParser import HTMLParser

#converts a string to a integer if the string is a integer, else returns None
def str2int(string):
    if string == None:  return None
    try:
        return int(string)
    except ValueError:
        return None

def getvalue(attrs):
    for attr in attrs:
        if attr[0] == 'value':
            return attr[1]
    return None



class qualis_extractor(object):
    #Constructor
    def __init__(self,online):
        self.online = online #extrair online ou offline ?
        self.publicacao = {} #{'nome pub',[ (1,'A1') ]}
        self.issn = {} #{'issn','nome pub'}
        self.areas = []
        
    def parseContent(self, html):
        """
        Process a html page containing qualis data
        Args:
            html: the document to be parsed.
            data: a list of lists containing the data parsed from the tables
        Return:
            1 if more pages exist
            0 if not
        """
        parsedhtml = BeautifulSoup(html)
        if parsedhtml == None:
            return
        
        tmp = parsedhtml.body
        table = None
        for tb in tmp.findAll('table'): #get the table with content
            for attr,val in tb.attrs:
                if attr == 'class' and val.find('rich-table') >= 0:
                    table = tb

        tmp = table
        
        if tmp != None: tmp = tmp.find('tbody') #get the body of the table
        if tmp != None: #get all rows
            tmp = tmp.findAll('tr')
        else:   return None
        #extract each line from all rows and add to a matrix with the values of the table
        for i in tmp:
            line = []
            for j in i.findAll('td'):
                stringtoadd = j.string
                if stringtoadd == None:
                    line.append('')
                else:
                    line.append(HTMLParser().unescape(stringtoadd))
            
            issn_qualis = line[0]
            titulo_qualis = line[1]
            extrato_qualis = line[2]
            area_qualis = line[3]
            
            if titulo_qualis == '':
                continue
            
            
            qualis = None
            
            if issn_qualis != '':
                qualis = self.issn.get(issn_qualis)
                
            if qualis == None:
                qualis = []
            
            qualis.append( (area_qualis,extrato_qualis) )
            
            if issn_qualis != None:
                self.issn[issn_qualis] = qualis
            
            self.publicacao[titulo_qualis] = qualis            
            
            #print issn_qualis,':',qualis
            
            
        if html.find('{\'page\': \'last\'}') != -1:
            return 1
            
        return 0
    
    def getAreas(self,html):
        self.areas = []
        parsedhtml = BeautifulSoup(html)
        select = parsedhtml.find('select')
        if select == None:
            return None
        options = select.findAll('option')
        for opt in options:
            name = opt.string
            index = str2int(getvalue(opt.attrs))
            if name != None and index != None:
                self.areas.append((index,name))
        
    def init_session(self):
        """
        Sao necessarias tres requisicoes iniciais para que se chegue a pagina
        que exibe a avaliacao dos artigos.
        """
        urlBase = "http://qualis.capes.gov.br/webqualis/"
        acessoInicial = requests.get(urlBase+'principal.seam')
        jid = acessoInicial.cookies['JSESSIONID']
        print 'Session ID: ',jid
        url1 = urlBase + "publico/pesquisaPublicaClassificacao.seam;jsessionid=" + jid + "?conversationPropagation=begin"
        req1 = urllib2.Request(url1)
        arq1 = urllib2.urlopen(req1)
        
        
        self.url2 = urlBase + "publico/pesquisaPublicaClassificacao.seam;jsessionid=" + jid
        
        if not self.online:
            req2 = urllib2.Request(self.url2, 'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn=&javax.faces.ViewState=j_id2&consultaPublicaClassificacaoForm%3Aj_id192=consultaPublicaClassificacaoForm%3Aj_id192')
            arq2 = urllib2.urlopen(req2)
            #get all the areas of qualis
            self.getAreas(arq2.read())
            req3 = urllib2.Request(self.url2, 'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=0&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&consultaPublicaClassificacaoForm%3AbtnPesquisarTituloPorArea=Pesquisar&javax.faces.ViewState=j_id2')
            arq3 = urllib2.urlopen (req3)
        
            
    
    def extract_qualis(self,areas): 
        #extract all the areas
        for area in areas:#areaskeys:
            scroller = 1
            more = 1
            reqn = urllib2.Request(self.url2, 'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=' + str(area) + '&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&consultaPublicaClassificacaoForm%3AbtnPesquisarTituloPorArea=Pesquisar&javax.faces.ViewState=j_id2')
            
            arqn = urllib2.urlopen (reqn)
            data = []
            print 'Extracting from Area: ',area,' - ',self.Areas[area]
            while more == 1:
                print "Page:", scroller 
            
                reqn = urllib2.Request(self.url2, 'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=' + str(area) + '&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&javax.faces.ViewState=j_id3&ajaxSingle=consultaPublicaClassificacaoForm%3AscrollerArea&consultaPublicaClassificacaoForm%3AscrollerArea=' + str(scroller) + '&AJAX%3AEVENTS_COUNT=1&')
                
                #arqn = urllib2.urlopen (reqn)
                ntries = 10
                for i in range(0,ntries):
                    try:
                        arqn = urllib2.urlopen(reqn)
                        break # success
                    except urllib2.URLError as err:
                        print "Error occurried. Trying again."
                        continue
                        #if not isinstance(err.reason, socket.timeout):
                        #    raise "Non timeout error occurried while loading page." # propagate non-timeout errors
                        #else: # all ntries failed 
                        #    raise err # re-raise the last timeout error
                    if i == 10:
                        print "ja tentou 10 vezes!"
                        break
        
                htmln = arqn.read()
                more = self.parseContent(htmln,area)
                scroller += 1
            
            
            
    def load_data(self):
        f = open('data','r')
        data = pickle.load(f)
        self.issn = data[0]
        self.publicacao = data[1]
        self.Areas = data[2]
        f.close() 
    
    def save_data(self): 
        f = open('data','w')
        data = (self.issn,self.publicacao,self.Areas)
        pickle.dump(data,f)
        f.close()
    
    def get_area_by_name(self,name):
        for i in self.areas:
            print i[1],'->',name
            if i[1].upper() == name.upper():
                return i
    
    def get_area_by_cod(self,cod):
        for i in self.areas:
            if i[0] == cod:
                return i
    
    
    #get a qualis by issn        
    def get_qualis_by_issn(self,issn):
        if self.online:
            print 'Getting qualis online...'
            req = urllib2.Request(self.url2,'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn='+issn+'&consultaPublicaClassificacaoForm%3AbtnPesquisarISSN=Pesquisar&javax.faces.ViewState=j_id2') 
            for i in range(0,10):
                try:
                    arqn = urllib2.urlopen(req)
                    break # success
                except urllib2.URLError as err:
                    print "Error occurried. Trying again."
                    continue
                    if i == 10:
                        print "ja tentou 10 vezes!"
                        break
            
            html = arqn.read()
            
            self.parseContent(html)
                
        
        return self.issn.get(issn)
    #get a qualis by the name
    def get_qualis_by_name(self,name):
        return self.publicacoes.get(name)
    

#extractor = qualis_extractor(0)
#extractor.init_session()
#print extractor.areas
#for i,j in extractor.get_qualis_by_issn('1993-8233'):
#    print i,'=',j
#extractor.save_data()
