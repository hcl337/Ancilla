import gfm


with open( '../API.md') as f:
    with open( 'outer.html') as outer:
        w = open('testdocs.html', 'w')
        #w.write( outer.read().replace("{{MARKDOWN}}", md( f.read()))  )
        words =  gfm.markdown( f.read() )

        # Make code format correctly
        words = words.replace('</code></p>', '</code></pre>')
        words = words.replace('<p><code>', '<pre><code>')
        # Get rid of the js tags on it
        words = words.replace('<code>js', '<code>')

        w.write( outer.read().replace("{{MARKDOWN}}", words) )
        #w.write( gfm.markdown( f.read()))

