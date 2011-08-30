#!/usr/bin/python
# -*- coding: utf-8  -*-
 
"""
This is not a complete bot; rather, it is a template from which simple
bots can be made. You can rename it to mybot.py, then edit it in
whatever way you want.

The following parameters are supported:

&params;

-dry              If given, doesn't do any real changes, but only shows
                  what would have been changed.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""
#
# (C) Pywikipedia bot team, 2006-2010
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: basic.py 8589 2010-09-22 05:07:29Z xqt $'
#

import wikipedia as pywikibot
import pagegenerators
import re
import editarticle
import sys
from datetime import datetime
import imdb
import filmfunctions
import difflib
import codecs
import itertools

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class FilmBot:
    # Edit summary message that should be used.
    # NOTE: Put a good description here, and add translations, if possible!
    msg = {
        'ar': u'روبوت: تغيير ...',
        'cs': u'Robot změnil ...',
        'de': u'Bot: Ändere ...',
        'en': u'Robot: Changing ...',
        'fa': u'ربات: تغییر ...',
        'fr': u'Robot: Changé ...',
        'ja':u'ロボットによる：編集',
        'ksh': u'Bot: Änderung ...',
        'nds': u'Bot: Ännern ...',
        'nl': u'Bot: wijziging ...',
        'pl': u'Bot: zmienia ...',
        'pt': u'Bot: alterando...',
        'sv': u'Bot: Ändrar ...',
        'zh': u'機器人：編輯.....',
    }

    def __init__(self, generator, dry):
        """
        Constructor. Parameters:
            * generator - The page generator that determines on which pages
                          to work on.
            * dry       - If True, doesn't do any real changes, but only shows
                          what would have been changed.
        """
        self.generator = generator
        self.dry = dry
        self.imdbNum = 0
        self.templateRegex = re.compile("{{.*}}") #This is how templates are in wikipedia
        self.referenceRegex = re.compile("(<ref.*?/(ref)?>)+")
        self.commentRegex = re.compile("<!--.*?-->")
        self.wikilinkRegex = re.compile("\[\[.*\|.*\]\]")
        self.log = codecs.open('log.txt', 'w', 'utf-8')
        # Set the edit summary message
        self.summary = pywikibot.translate(pywikibot.getSite(), self.msg)
        linktrail = pywikibot.getSite().linktrail()
        self.linkR = re.compile(r'\[\[(?P<title>[^\]\|#]*)(?P<section>#[^\]\|]*)?(\|(?P<label>[^\]]*))?\]\](?P<linktrail>' + linktrail + ')')
        #Gets the infobox template from the documentation page.
        infoTemp = pywikibot.Page(pywikibot.getSite(), "Template:Infobox_film/doc").get()
        infoTempStart = infoTemp.find("{{Infobox film") + 2
        bracketCount = 2
        infoTempEnd = infoTempStart
        while bracketCount != 0 :
          infoTempEnd += 1
          if infoTemp[infoTempEnd:infoTempEnd+1] == "{":
            bracketCount += 1
          elif infoTemp[infoTempEnd:infoTempEnd+1] == "}":
            bracketCount -= 1
        self.infoboxTemplate = infoTemp[infoTempStart - 2:infoTempEnd+1]
        
        #Old way to do it with the template written out on the page with triple "{" in the infos
        #pywikibot.replaceExcept(re.search("{{Infobox film.*?[^}]}}[^}]", pywikibot.Page(pywikibot.getSite(), "Template:Infobox_film/doc").get(), re.S).group(), r"{{{.*?}}}", "", "")
        
    def run(self):
        for page in self.generator:
            self.treat(page)
            
    def treat(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        text = self.load(page)
        if not text:
            return

        #Fix the plot heading
        if(re.search("([\r\n]|^)\=+ *(t|T)he (P|p)lot *\=+", text)):
          text = pywikibot.replaceExcept(text, r"([\r\n]|^)\=+ *(t|T)he (P|p)lot *\=+", re.sub(" *\w+ *\w+ *", " Plot ", re.search("([\r\n]|^)\=+ *(t|T)he (P|p)lot *\=+", text).group()), ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        #fix external link heading
        if(re.search("([\r\n]|^)\=+ *External Links *\=+", text)):
          text = pywikibot.replaceExcept(text, r"([\r\n]|^)\=+ *External Links *\=+", re.sub(" *\w+ *\w+ *", " External links ", re.search("([\r\n]|^)\=+ *External Links *\=+", text).group()), ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        #fix awards heading to accolades
        if(re.search("([\r\n]|^)\=+ *(A|a)wards *\=+", text)):
          text = pywikibot.replaceExcept(text, r"([\r\n]|^)\=+ *(A|a)wards *\=+", re.sub(" *\w+ *", " Accolades ", re.search("([\r\n]|^)\=+ *(A|a)wards *\=+", text).group()), ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        #fix dvd release to home media
        if(re.search("([\r\n]|^)\=+ *(DVD|dvd) (R|r)elease *\=+", text)):
          text = pywikibot.replaceExcept(text, r"([\r\n]|^)\=+ *(DVD|dvd) (R|r)elease *\=+", re.sub(" *\w+ \w+ *", " Home media ", re.search("([\r\n]|^)\=+ *(DVD|dvd) (R|r)elease *\=+", text).group()), ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        #unwiki-link united states
        text = pywikibot.replaceExcept(text, r"\[\[(U|u)nited (S|s)tates\]\]", "United States", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        #unwiki-link film
        text = pywikibot.replaceExcept(text, r"\[\[film\]\]", "film", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        text = pywikibot.replaceExcept(text, r"\[\[Film\]\]", "Film", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        text = pywikibot.replaceExcept(text, r"{{(Rottentomatoes|Rotten Tomatoes|Rotten tomatoes)", "{{Rotten-tomatoes", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        text = pywikibot.replaceExcept(text, r"{{(IMDB title|IMDBtitle|IMDb Title|Imdb movie|Imdb title|Imdb-title|Imdbtitle|imdb title)", "{{IMDb title", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        text = pywikibot.replaceExcept(text, r"{{(Amg title|Amg movie|Allmovie)\|", "{{AllRovi movie|", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        if(re.search("\[\[[0-9]{4} in film\|[0-9]{4}\]\]", text)):
          text = text[:re.search("\[\[[0-9]{4} in film\|[0-9]{4}\]\]", text).start()]+self.removeWikilink(text[re.search("\[\[[0-9]{4} in film\|[0-9]{4}\]\]", text).start():re.search("\[\[[0-9]{4} in film\|[0-9]{4}\]\]", text).end()]) + text[re.search("\[\[[0-9]{4} in film\|[0-9]{4}\]\]", text).end():]
        
        ####self.imdbNum = 
        if re.subn("{{IMDb title.*?}}", "", text)[1] == 1: #If there is only 1 imdb link on the page search for the info
          if re.search("[0-9]{6,7}", re.search("{{IMDb title.*?}}", text).group()):
            self.imdbNum = re.search("[0-9]{6,7}", re.search("{{IMDb title.*?}}", text).group()).group()
        else:
          self.imdbNum = 0
          
        #fix bad template names for infobox film
        text = pywikibot.replaceExcept(text, r"((I|i)nfobox Film|(I|i)nfobox (M|m)ovie|(I|i)nfobox_(f|F)ilm)", "Infobox film", ['comment', 'includeonly', 'math', 'noinclude', 'nowiki', 'pre', 'source', 'ref', 'timeline'])
        
        infoboxStart = text.find("Infobox film")
        #get infobox that is there.
        if infoboxStart != -1: #infobox exists
          #find the end of the infobox but must account for other templates that are inside the infobox. Search for ending brackets by each character. For each
          #  new open bracket found add 1, then when finding ending brackets remove 1. This will find the ending position of the infobox while ignoring any
          #  and ALL templates that are found inside. Regex doesn't work here :(
          bracketCount = 2
          infoboxEnd = infoboxStart
          while bracketCount != 0 :
            infoboxEnd += 1
            if text[infoboxEnd:infoboxEnd+1] == "{":
              bracketCount += 1
            elif text[infoboxEnd:infoboxEnd+1] == "}":
              bracketCount -= 1
          infobox = text[infoboxStart:infoboxEnd-1]
          text = text[:infoboxStart-2] + self.infoboxCleanup(infobox) + text[infoboxEnd+1:] #replace old infobox with new one and put it where the old one was.
        elif(text.find(r"(i|I)nfobox") != -1): #infox doesn't exists
          text = text #self.infoboxTemplate + text
          
        if not self.save(text, page, self.summary):
          pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))
          
          #pywikibot.output(text.encode('utf-8', 'replace'))
          
    def logDiff(self, oldtext, newtext):
      # This is probably not portable to non-terminal interfaces....
      # For information on difflib, see http://pydoc.org/2.3/difflib.html
      color = {
          '+': '',
          '-': '',
      }
      diff = u''
      colors = []
      # This will store the last line beginning with + or -.
      lastline = None
      # For testing purposes only: show original, uncolored diff
      #     for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
      #         print line
      for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
          if line.startswith('?'):
              # initialize color vector with None, which means default color
              lastcolors = [None for c in lastline]
              # colorize the + or - sign
              lastcolors[0] = color[lastline[0]]
              # colorize changed parts in red or green
              for i in range(min(len(line), len(lastline))):
                  if line[i] != ' ':
                      lastcolors[i] = color[lastline[0]]
              diff += lastline + '\n'
              # append one None (default color) for the newline character
              colors += lastcolors + [None]
          elif lastline:
              diff += lastline + '\n'
              # colorize the + or - sign only
              lastcolors = [None for c in lastline]
              lastcolors[0] = color[lastline[0]]
              colors += lastcolors + [None]
          lastline = None
          if line[0] in ('+', '-'):
              lastline = line
      # there might be one + or - line left that wasn't followed by a ? line.
      if lastline:
          diff += lastline + '\n'
          # colorize the + or - sign only
          lastcolors = [None for c in lastline]
          lastcolors[0] = color[lastline[0]]
          colors += lastcolors + [None]

      result = u''
      lastcolor = None
      for i in range(len(diff)):

          lastcolor = colors[i]
          result += diff[i]
      return result

    def load(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None

    def save(self, text, page, comment, minorEdit=True, botflag=True):
        # only save if something was changed
        if text != page.get():
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            pywikibot.showDiff(page.get(), text)
            
            self.log.write("======" + page.title() + "======\n")
            self.log.write(self.logDiff(page.get(), text))
            self.log.write("\n\n")
            self.log.write(text)
            
            #choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
            
            pywikibot.output(u'Comment: %s' %comment)
            if not self.dry:
                choice = pywikibot.inputChoice(
                    u'Do you want to accept these changes?',
                    ['Yes', 'No'], ['y', 'N'], 'N')
                if choice == 'y':
                    try:
                        # Save the page
                        page.put(text.encode('utf-8', 'replace'), comment=comment,
                                 minorEdit=minorEdit, botflag=botflag)
                    except pywikibot.LockedPage:
                        pywikibot.output(u"Page %s is locked; skipping."
                                         % page.title(asLink=True))
                    except pywikibot.EditConflict:
                        pywikibot.output(
                            u'Skipping %s because of edit conflict'
                            % (page.title()))
                    except pywikibot.SpamfilterError, error:
                        pywikibot.output(
                            u'Cannot change %s because of spam blacklist entry %s'
                            % (page.title(), error.url))
                    else:
                        return True
        return False
        
    #remove any possible wikilinks by searching through them one at a time
    def removeWikilink(self, data):
      while(data.find("[[") != -1):
        bracketCount = 1
        wLinkStart = data.find("[[")
        wLinkEnd = wLinkStart
        while bracketCount != 0 :
          wLinkEnd += 1
          if data[wLinkEnd:wLinkEnd+1] == "[":
            bracketCount += 1
          elif data[wLinkEnd:wLinkEnd+1] == "]":
            bracketCount -= 1
        wLink = data[wLinkStart:wLinkEnd+1]
        if(re.search("\|.*?\]\]", wLink)) : 
          wLink = re.search("\|.*?\]\]", wLink).group().replace("|", "").replace("]]", "")
        elif(re.search("\[\[.*?\]\]", wLink)):
          wLink = re.search("\[\[.*?\]\]", wLink).group().replace("[[", "").replace("]]", "")
        data = data[:wLinkStart] + wLink + data[wLinkEnd+1:]
      return data
    
    #Cleanup the infobox: add missing fields, correct data, remove typically unused params
    def infoboxCleanup(self, infobox):
      infobox = infobox.replace("<br />", "<br>") #convert old style breaks to new style
      infobox = infobox.replace("<br/>", "<br>") #convert old style breaks to new style
      infobox = infobox.replace("<BR>", "<br>") #convert old style breaks to new style
      newBox = self.infoboxTemplate
      infoSplit = re.sub("<ref.*?/(ref)?>", " reference ", re.sub("{{.*}}", "template", infobox)).split("|")
      for field in infoSplit:
        try: field.split("=")[1]
        except IndexError:
          sys.exc_clear() #skip it if there is an index error, means it has no "=", invalid field
        else:
          if(field.split("=")[1].strip() != ""): #only extract fields with info
            #The info is going to be inserted into the new infobox, I find where the equals sign exists for the field where I'm inserting the info
            fieldRegex = re.compile(field.split("=")[0].lower().strip()+"[^\|]*?=", re.I) #find the field but it can't have a | after. This will ensure I get a field and not the data
            temp = fieldRegex.search(newBox)
            #first try and find where it should go in the new infobox
            try: equals = newBox.find("=", temp.start())
            except:
              equals = -1
            #but then make sure to check that it is not inside any wiki templates/refs that have been placed inside the new infobox.
            insideWiki = True
            while(insideWiki):
              insideWiki = False
              searches = itertools.chain(self.commentRegex.finditer(newBox), self.referenceRegex.finditer(newBox), self.templateRegex.finditer(newBox), self.wikilinkRegex.finditer(newBox)) #create a combine iterator
              for search in searches: 
                try: 
                  if(equals > search.start() and equals < search.end()):
                    try: equals = newBox.find("=", fieldRegex.search(newBox, search.end()).start()) #I need where we're place in the information in the new infobox
                    except:
                      equals = -1
                    insideWiki = True
                except:
                  sys.exc_clear()
            try: oldEquals = infobox.find("=", fieldRegex.search(infobox).start()) #I need where the information starts in the old infobox
            except:
              oldEquals = -1
            if(equals != -1 and oldEquals != -1): #if an old field is not used, do not copy it over
              #This used to be silly but now it's quite reasonable. Loop through and check against every search to make sure
              # that the equals sign is not inside any wiki-stuff.
              insideWiki = True
              y = oldEquals + 1
              x = infobox.find("=", y) #find the next equals
              while(insideWiki):
                insideWiki = False
                searches = itertools.chain(self.commentRegex.finditer(infobox), self.referenceRegex.finditer(infobox), self.templateRegex.finditer(infobox), self.wikilinkRegex.finditer(infobox))
                for search in searches: 
                  #pywikibot.output(str(x) + " " + str(search.start()) + " " + str(search.end()))
                  try: 
                    if(x > search.start() and x < search.end()):
                      insideWiki = True
                      y = x + 1
                      x = infobox.find("=", y)
                  except:
                    sys.exc_clear()
                #if it wasn't inside any of the wiki-stuff then it's ok to grab it
                if(x == -1 and not insideWiki):
                  data = infobox[oldEquals+1:].strip()
                  while(data[len(data)-1:] == "|"):
                    data = data[:len(data)-1].strip()
                elif(not insideWiki):
                  data = infobox[oldEquals+1:infobox.rfind("|", oldEquals, infobox.find("=", x))].strip()
              #pywikibot.output(field.split("=")[0].strip().lower() + ": " + data)

              #This will take care of any references and comments on the data
              refs = "" #initialize
              if self.referenceRegex.search(data) : #remove the ref and save it for later so I can format the date
                refs += data[self.referenceRegex.search(data).start():self.referenceRegex.search(data).end()]
                data = re.sub(self.referenceRegex, "", data)
              if self.commentRegex.search(data) :
                refs += data[self.commentRegex.search(data).start():self.commentRegex.search(data).end()]
                data = re.sub(self.commentRegex, "", data)

              data = re.sub(",<br>", "<br>", data) #if there are commas and line breaks, oh my
              if(field.split("=")[0].strip().lower() == "language"): #if the language is linked, unlink it.
                data = self.removeWikilink(data)
              elif(field.split("=")[0].strip().lower() == "country" and not re.search("image:flag", data.lower()) and not re.search("file:flag", data.lower())):
                #data = re.sub("<br>", ", ", data) Do I have to convert to commas?
                data = self.removeWikilink(data)
                data = filmfunctions.countryToTemplate(data)
              elif(field.split("=")[0].strip().lower() == "released" and re.search("{{start date.*?}}", data.lower())):
                data = re.sub("start", "film", data, 0, re.I)
              elif(field.split("=")[0].strip().lower() == "released" and re.search("{{filmdate.*?}}", data.lower())):
                data = re.sub("filmdate", "film date", data)
              elif(field.split("=")[0].strip().lower() == "released" and not re.search("{{film date.*?}}", data.lower()) and data.find("<br>") == -1):
                data = self.formatDate(data)
              elif(field.split("=")[0].strip().lower() == "runtime") :
                data = self.removeWikilink(data)
                data = re.sub("(min(\.)|mins\.|mins|min)(?!utes)", "minutes", data)
              elif(field.split("=")[0].strip().lower() == "distributor"):
                data = re.sub("{{flag.?icon.*?}}", "", data, 0, re.I).strip()
                
              data += refs #attach the references and comments again
                
              #Break it down: Take everything before where I want to insert the info + the old info I found between the equals sign and the last "|" + everything
              #  after where I insert the data.
              #pywikibot.output(field.split("=")[0] + " " + data)
              newBox = newBox[:equals+2] + data + newBox[equals+2:]
              #pywikibot.output(newBox)
              #choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
              
      if(self.imdbNum != 0):
        newBox = self.addImdbInfo(newBox)
        
      #remove typically unused parameters
      if re.search("\| image size *=.*?\n", newBox).group().split("=")[1].strip() == "" :
        newBox = re.sub("\| image size *=.*?\n", "", newBox)
      if re.search("\| narrator *=.*?\n", newBox).group().split("=")[1].strip() == "" :
        newBox = re.sub("\| narrator *=.*?\n", "", newBox)
      if re.search("\| border *=.*?\n", newBox).group().split("=")[1].strip() == "" :
        newBox = re.sub("\| border *=.*?\n", "", newBox)
        
      if re.search("\| alt *=.*?\n", newBox).group().split("=")[1].strip() == "" :
        newBox = re.sub("\| alt *=.*?\n", "| alt            = <!-- see WP:ALT -->\n", newBox)
      if re.search("\| based on *=.*?\n", newBox).group().split("=")[1].strip() == "" :
        newBox = re.sub("\| based on *=.*?\n", "| based on       = <!-- {{based on|title of the original work|writer of the original work}} -->\n", newBox)
      if re.search("\| released *=.*?\n", newBox).group().split("=")[1].strip() == "" :
        newBox = re.sub("\| released *=.*?\n", "| released       = <!-- {{Film date|Year|Month|Day|Location}} -->\n", newBox)
      
      return newBox.strip()
      
    def addImdbInfo(self, infobox):
      movie = imdb.IMDb().get_movie(self.imdbNum)
      for field in re.sub("<ref.*?/(ref)?>", " reference ", re.sub("{{.*}}", "template", infobox)).split("|"):
        data = ""
        try: field.split("=")[1]
        except IndexError:
          sys.exc_clear() #skip it if there is an index error, means it has no "=", invalid field
        else:
          if(field.split("=")[1].strip() == ""): #fill in fields without data
            if(field.split("=")[0].strip() == "director"):
              if movie.get('director'):
                for name in movie.get('director'):
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            elif(field.split("=")[0].strip() == "producer"):
              if movie.get('producer'):
                for name in movie.get('producer')[0:2]:
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:]                 
            elif(field.split("=")[0].strip() == "starring"):
              if movie.get('cast'):
                for name in movie.get('cast')[0:4]:
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:]                 
            elif(field.split("=")[0].strip() == "music"):
              if movie.get('original music'):
                for name in movie.get('original music')[0:2]:
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:]                 
            elif(field.split("=")[0].strip() == "cinematography"):
              if movie.get('cinematographer'):
                for name in movie.get('cinematographer')[0:2]:
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:]                 
            elif(field.split("=")[0].strip() == "editing"):
              if movie.get('editor'):
                for name in movie.get('editor')[0:2]:
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:]                 
            elif(field.split("=")[0].strip() == "studio"):
              if movie.get('studio'):
                for name in movie.get('studio')[0:2]:
                  data += name['name'] + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:]                 
            elif(field.split("=")[0].strip() == "released"):
              if movie.get('release date'):
                for date in movie.get('release date'):
                  data += self.formatDate(date) + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            #elif(field.split("=")[0].strip() == "writer"):
            #  if movie.get('writer'):
            #    for name in movie.get('writer'):
            #      data += name['name'] + "+"
            #    infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            elif(field.split("=")[0].strip() == "runtime"):
              if movie.get('runtime'):
                try: 
                  if(movie.get('runtime')[0].split(":")[0].isdigit()):
                    infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + movie.get('runtime')[0].split(":")[0] + " minutes" + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
                except IndexError:
                  infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + movie.get('runtime')[0] + " minutes" + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            elif(field.split("=")[0].strip() == "country"):
              if movie.get('country'):
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + filmfunctions.countryToTemplate(movie.get('country')[0]) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            elif(field.split("=")[0].strip() == "language"):
              if movie.get('language'):
                for name in movie.get('language'):
                  data += name + "+"
                infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + re.sub("\+", "<br>", data.rstrip("+")) + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
              

      return infobox

    def formatDate(self, data):
      month = "" #initialize so if they are not used prints empty in template
      day = "" 
      options = ""
      origData = data #save so if we find out it's not really a date
      usDateRegex = re.compile("^(january|february|march|april|may|june|july|august|september|october|november|december).[0-9]{1,2}.[0-9]{4}$", re.I)
      euDateRegex = re.compile("^[0-9]{1,2}.(january|february|march|april|may|june|july|august|september|october|november|december) [0-9]{4}$", re.I)
      shortDateRegex = re.compile("^(january|february|march|april|may|june|july|august|september|october|november|december).[0-9]{4}$", re.I)
      #If the date is 3 different items without a place in parens.  I use the re.sub to replace the place with nothing, removing it from the date. I find the
      #  format by replacing the different items with their format name from datetime. Then compile it all into a film date template.
      data = re.sub("{{flag.?icon.*?}}", "", data, 0, re.I).strip() #remove any flagicons
      #remove the wikilinks if they exist
      if(data.find("[[") != -1):
        data = self.removeWikilink(data)
      #remove the "th" from any number in the date that might have it.
      if(re.search("[0-9]{2}th", data)):
        data = re.sub("[0-9]{2}th", data[data.find(re.search("[0-9]{2}th", data).group(0)):data.find(re.search("[0-9]{2}th", data).group(0))+2], data)
      data = re.sub("<small>", "", re.sub("</small>", "", data)) #remove any small tags
      data = re.sub(",", "", data) # remove any commas in the date format
      justDate = re.sub("\([.A-Za-z ]+\)", "", data).strip()
      #If after the wikilink removal it isn't a proper date just skip it.
      if(not (usDateRegex.search(justDate) or euDateRegex.search(justDate) or shortDateRegex.search(justDate) or justDate.isdigit())):
        return origData
      if(len(justDate.split()) == 3):
        format = re.sub("[0-9]{1,2}", "%d", re.sub("[0-9]{4}", "%Y", re.sub("[A-Za-z]+", "%B", justDate))) #convert what is in the data field to what format it is in datetime.
        date = datetime.strptime(justDate, format) #convert to date
        month = str(date.month)
        day = str(date.day)
      #if it's only 2 it's usually a year and a month
      elif(len(justDate.split()) == 2):
        format = re.sub("[0-9]{4}", "%Y", re.sub("[A-Za-z]+", "%B", justDate)) #convert what is in the data field to what format it is in datetime.
        date = datetime.strptime(justDate, format) #convert to date
        month = str(date.month)
      #only 1 item is usually just the year
      elif(len(justDate.split()) == 1 and justDate.isdigit()):
        format = re.sub("[0-9]{4}", "%Y", justDate) #convert what is in the data field to what format it is in datetime.
        date = datetime.strptime(re.sub("\([A-Za-z ]+\)", "", data).strip(), format) #convert to date
      #see if there is a place to add  
      try: re.search("\([.A-Za-z ]+\)", data).group()
      except AttributeError:
        place = ""
      else:
        place = re.search("\([.A-Za-z ]+\)", data).group().replace(")", "").replace("(", "")
      if(euDateRegex.search(justDate)): #if a EU date make the day appear first.
        options = "|df=y"
      data = "{{film date|"+str(date.year)+"|"+month+"|"+day+"|"+place+options+"}}"
      return data + " <!--{{Film date|year|month|day|location}}-->"
      
def main():
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []
    # If dry is True, doesn't do any real changes, but only show
    # what would have been changed.
    dry = False

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if arg.startswith("-dry"):
            dry = True
        else:
            # check if a standard argument like
            # -start:XYZ or -ref:Asdf was given.
            if not genFactory.handleArg(arg):
                pageTitleParts.append(arg)

    if pageTitleParts != []:
        # We will only work on a single page.
        pageTitle = ' '.join(pageTitleParts)
        page = pywikibot.Page(pywikibot.getSite(), pageTitle)
        gen = iter([page])

    if not gen:
        gen = genFactory.getCombinedGenerator()
    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
        bot = FilmBot(gen, dry)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
