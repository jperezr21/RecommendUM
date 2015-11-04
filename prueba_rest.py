#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2


if __name__ == '__main__':
    resultado = json.load(urllib2.urlopen(
        "https://api.themoviedb.org/3/search/movie?api_key=150d5e95df95be2e0c68094bc9d6241f&query=toy+story"))
    print resultado[u'results'][0]