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
# (C) Pywikipedia bot team, 2006-2011
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: basic.py 9359 2011-07-10 12:22:39Z xqt $'
#

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n
import re
import editarticle
import sys
from datetime import datetime
import imdb
import filmfunctions
import difflib
import codecs
import itertools
import urllib
import subprocess

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class BasicBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, dry):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
            @param dry: If True, doesn't do any real changes, but only shows
                        what would have been changed.
            @type dry: boolean.
        """
        self.generator = generator
        self.dry = dry
        self.imdbNum = "0"
        self.chrome = "C:\Documents and Settings\\Desktop\GoogleChromePortable\GoogleChromePortable.exe"
        self.list = codecs.open('HasImageList.txt', 'w', 'utf-8')
        # Set the edit summary message
        self.summary = i18n.twtranslate(pywikibot.getSite(), 'basic-changing')

    def run(self):
        for page in self.generator:
            self.treat(pywikibot.Page(pywikibot.getSite(), page.title().replace("Talk:", "")))
            

    def treat(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        text = self.load(page)
        if not text:
            return

        
        noSearch = 1;
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
                pywikibot.output("Already has image")
                noSearch = 1
                #self.list.write("Talk:"+page.title().replace(" ", "_").encode('utf-8', 'replace')+"\n")
                Chrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+page.title().replace(" ", "_").encode('utf-8', 'replace'))
                Chrome3 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/w/index.php?title=Talk:"+page.title().replace(" ", "_").encode('utf-8', 'replace')+"&action=edit")
                choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
        elif(text.find(r"(i|I)nfobox") != -1): #infox doesn't exists
          pywikibot.output("Page doesn't have an infobox")
        
        if noSearch == 0 :
          ####self.imdbNum = 
          if re.subn("{{imdb title.*?}}", "", text.lower())[1] == 1: #If there is only 1 imdb link on the page search for the info
            if re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()):
              self.imdbNum = re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()).group()
          
              f = urllib.urlopen("http://www.movieposterdb.com/browse/search?type=movies&query="+self.imdbNum)
              s = f.read()
              f.close()
              if(s.find("No movies found.") == -1):
                pywikibot.output("YES!  " + page.title())
                spChrome = subprocess.Popen(self.chrome+' '+"http://www.movieposterdb.com/browse/search?type=movies&query="+self.imdbNum)
                spChrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+page.title().replace(" ", "_").encode('utf-8', 'replace'))
                choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
              else:
                pywikibot.output("No Image \""+page.title().encode('utf-8', 'replace')+"\" -> IMDB = "+self.imdbNum)
          else:
            pywikibot.output("No IMDB link   " + page.title().encode('utf-8', 'replace') + "   " + self.imdbNum)
          
        
        #if not self.save(text, page, self.summary):
        #    pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))

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
            pywikibot.output(u'Comment: %s' %comment)
            pywikibot.showDiff(page.get(), text)
            if not self.dry:
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
        return False

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
        bot = BasicBot(gen, dry)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
