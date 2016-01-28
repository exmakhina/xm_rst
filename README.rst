######
xm_rst
######


Usage
#####

.. code:: bash

   xm_rst --help


Installation
############


Requirements:

- docutils
- argcomplete


Simply:

.. code:: bash

   mkdir -p ~/.local/opt{,/bin}
   pushd ~/.local/opt
   git clone ...
   pushd bin
   ln -sf ../xm_rst/xm_rst.py xm_rst
   popd
   popd


And you can add to your environment, if not already there:

.. code:: bash

   PATH+=~/.local/opt/bin

And some command-line completion:

.. code:: bash

   eval "$(register-python-argcomplete xm_rst 2>/dev/null)"
   


License
#######

MIT
