#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
The following parameters are supported:

&params;

-htm              Will create an html fil that has links for pages needing changes
                  and links to image searches.
-wiki             Print a list of possible results but in a wikiformat

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n
import re
import editarticle
import sys
import codecs
import urllib
import subprocess
import Film
import msvcrt
import filmfunctions
import imdb

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class FilmImageBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, html, wiki):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
        """
        self.generator = generator
        self.imdbNum = "0"
        self.chrome = filmsettings.getChrome()
        # Set the edit summary message
        self.summary = i18n.twtranslate(pywikibot.getSite(), 'basic-changing')
        self.hasImagestack = []
        self.newImageDict = dict()
        self.html = html
        self.wiki = wiki
        self.file = codecs.open('filmImages.html', 'w', 'utf-8')

    def run(self):
      for page in self.generator:
        text = self.load(page)
        code = self.treat(text, page)
        title = page.title()
        pywikibot.output(title)
        if code == "has":
          pywikibot.output("Already has image")
          ###ALREADY HAS IMAGE LOGIC#####
          if self.html:
            self.file.write('<a href="https://secure.wikimedia.org/wikipedia/en/wiki/'+title.replace(" ", "_")+'">'+title+'</a><br />'+"\n")
          elif self.wiki:
            self.file.write("#"+page.title(asLink=True) + " has image\n")
          else:
            self.doHasImage(title, page.toggleTalkPage())
        elif code == "found":
          pywikibot.output("YES!")
          ####HAS NEW IMAGE LOGIC#####
          if self.html:
            self.file.write('<a href="https://secure.wikimedia.org/wikipedia/en/wiki/'+title.replace(" ", "_")+'">'+title+'</a> -> <a href="+http://www.movieposterdb.com/search/?query='+self.imdbNum+'">Image</a><br />'+"\n")
          elif self.wiki:
            self.file.write("#"+page.title(asLink=True) + ' [http://www.movieposterdb.com/search/?query='+self.imdbNum + " movieposterdb]\n")
          else:
            #self.newImageDict[title.replace(" ", "_")] = self.imdbNum
            self.doNewImage(title, page.toggleTalkPage())
        elif code == "noimagefound":
          pywikibot.output("No Image found -> IMDB = "+self.imdbNum)
        elif code == "noimdb":
          pywikibot.output("No IMDB link  " + self.imdbNum)
        elif code == "noinfobox":
          pywikibot.output("Page doesn't have an infobox")
   
    def kbfunc(self):
      return msvcrt.getch() if msvcrt.kbhit() else "Z"
      
    def doNewImage(self, title, talkPage):
      filmBot = Film.FilmBot(iter([pywikibot.Page(pywikibot.getSite(), title)]), True, False)
      filmBot.run()
      dis = ""
      movie = imdb.IMDb().get_movie(self.imdbNum)
      if movie.get('year'):
        year = movie.get('year')
      if movie.get('distributors'):
        pywikibot.output(str(len(movie.get('distributors'))))
        for name in movie.get('distributors')[0:1]:
          dis += name.get('name')

      self.writeRationale(title, year, dis)
      spNotepad = subprocess.Popen('notepad C:\pywikipedia\\filmImages.txt')

      spChrome = subprocess.Popen(self.chrome+' '+"http://www.movieposterdb.com/search/?query="+self.imdbNum)
      spChrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+title.replace(" ", "_").encode('utf-8', 'replace'))
      
      text = self.load(talkPage)
      text = text.replace("|needs-image=yes", "")
      self.save(text, talkPage, "update film banner (has image)")
      
    def doHasImage(self, title, talkPage):
      Chrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+title.replace(" ", "_").encode('utf-8', 'replace'))
      text = self.load(talkPage)
      text = text.replace("|needs-image=yes", "")
      self.save(text, talkPage, "update film banner (has image)")
      
    def writeRationale(self, title, year, dis):
      rationale = codecs.open('filmImages.txt', 'w', 'utf-8')
      rationale.write('{{Non-free use rationale\n')
      rationale.write('| Description       = Poster for \'\'[['+title+']]\'\', Copyright '+str(year)+' by '+dis+'. All Rights Reserved.\n')
      rationale.write('| Source            = [ MoviePosterDB.com]\n')
      rationale.write('| Article           = '+title+"\n")
      rationale.write('| Portion           = Small portion of commercial product\n| Low_resolution    = Yes\n| Purpose           = Serves as "cover art" to identify the article\'s topic\n| Replaceability    = No\n| other_information = \n}}')
      rationale.close
    
    def treat(self, text, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        if not text:
            return
        
        noSearch = 0;
        ###FIND IF TEXT HAS IMAGE
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
          infoSplit = re.sub("<ref.*?/(ref)?>", " reference ", re.sub("{{.*}}", "template", infobox)).split("|")
          for field in infoSplit:
            try: field.split("=")[1]
            except IndexError:
              sys.exc_clear() #skip it if there is an index error, means it has no "=", invalid field
            else:
              if field.split("=")[0].strip() == "image" and not field.split("=")[1].strip() == "":
                noSearch = 1
                return "has"
        #if infobox doesn't exist
        elif not (re.search("infobox film", text, re.I) or re.search("infobox_film", text, re.I) or re.search("infobox korean film", text, re.I) or re.search("infobox japanese film", text, re.I)):
          return "noinfobox"
        
        if noSearch == 0 :
          if re.subn("{{imdb title.*?}}", "", text.lower())[1] == 1: #If there is only 1 imdb link on the page search for the info
            if re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()):
              self.imdbNum = re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()).group()
          
              f = urllib.urlopen("http://www.movieposterdb.com/search/?query="+self.imdbNum)
              s = f.read()
              f.close()
              if(s.find("No results") == -1):
                return "found"
              else:
                return "noimagefound"
          else:
            return "noimdb"
          
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
      
    def save(self, text, page, comment, minorEdit=False, botflag=False):
        # only save if something was changed
        if text != page.get():
          # Show the title of the page we're working on.
          # Highlight the title in purple.
          pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                           % page.title())
          # show what was changed
          pywikibot.showDiff(page.get(), text)
          
          pywikibot.output(u'Comment: %s' %comment)
          choice = pywikibot.inputChoice(
            u'Do you want to accept these changes?',
            ['Yes', 'No'], ['y', 'N'], 'N')
          if choice == 'y':
            try:
                # Save the page
                page.put(text, comment=comment,
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
          #else:
          #  Chrome3 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/w/index.php?title=Talk:"+title+"&action=edit")
                  
        return False

def main():
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    html = False
    wiki = False
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
      if arg.startswith("-htm"):
        html = True
      elif arg.startswith("-wiki"):
        wiki = True
      else:
        if arg.startswith("-reg"):
          arg = '-cat:Film articles needing an image'
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
        gen = pagegenerators.PreloadingGenerator(filmfunctions.PagesFromTalkPagesGenerator(gen))
        bot = FilmImageBot(gen, html, wiki)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
