import random
import os

content = []

orig_file = 'newItems.txt'
working_file = 'newItems.txt~'

with open( orig_file ) as f, open( working_file, 'w+' ) as working:
    content = f.readlines()
    entity_url = random.choice( content ).strip( '\n' )
    print entity_url

    for line in content:
        if entity_url not in line:
            working.write( line )

os.rename( working_file, orig_file )
