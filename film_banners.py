#!/usr/bin/python

"""
The following parameters are supported:

&params;

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n
import re
import subprocess

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class FilmBannerBot:

  def __init__(self, generator):
    self.generator = generator
    self.chrome = "C:\Documents and Settings\\Desktop\GoogleChromePortable\GoogleChromePortable.exe"
    
  def run(self):
    for page in self.generator:
      #pywikibot.output(page.title())
      self.check(pywikibot.Page(pywikibot.getSite(), "Talk:"+page.title().replace("Talk:", "")))
  
  def check(self, talkPage):
    text = self.load(talkPage)
    if not text:
      self.open(talkPage)
    elif not re.search("\{\{(wp|wikiproject)?.?film", text.lower()):
      self.open(talkPage)
    #else:
    #  pywikibot.output(u"Page %s is fine; skipping."
    #                     % talkPage.title(asLink=True))
  
  def open(self, talkPage):
    Chrome = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+talkPage.title().replace(" ", "_").encode('utf-8', 'replace')+"?action=edit")
    
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

def main():
  genFactory = pagegenerators.GeneratorFactory()
  # The generator gives the pages that should be worked upon.
  gen = None
  pageTitleParts = []
  
  for arg in pywikibot.handleArgs():
    if arg.startswith("-reg"):
      arg = '-transcludes:Infobox film'
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
      bot = FilmBannerBot(gen)
      bot.run()
  else:
      pywikibot.showHelp()
    


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()