#!/usr/bin/python
"""
No parameters are supported.

Run as upkeep on categories already fully run with the bots
"""

import wikipedia as pywikibot
import pagegenerators
import Film
import film_banners as Banner


def main():
  genFactory = pagegenerators.GeneratorFactory()
  args = []
  # The generator gives the pages that should be worked upon.
  for x in range(2010, 2019):
    args.append('-cat:'+str(x)+" films")
  
  args.append('-cat:Upcoming films')
  
  for t in args:
    gen = None
    pageTitleParts = []
  
    for arg in pywikibot.handleArgs(t):
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
        filmBot = Film.FilmBot(gen, True)
        filmBot.run()
        bannerBot = Banner.FilmBannerBot(gen)
          bannerBot.run()
      
if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()