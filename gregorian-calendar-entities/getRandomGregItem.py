import random
import os

content = []

orig_file = 'gregItems-user.txt'
working_file = 'gregItems-user.txt~'

with open( orig_file ) as f, open( working_file, 'w+' ) as working:
    content = f.readlines()
    urls = random.choice( content ).strip( '\n' )
    print urls

    for line in content:
        if urls not in line:
            working.write( line )

os.rename( working_file, orig_file )
