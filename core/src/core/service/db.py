# -*- coding: utf-8 -*-
# -*- python -*-
#
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2014 INRIA - CIRAD - INRA
#
#       File author(s): Guillaume Baty <guillaume.baty@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################


def get(uri, path=None, force=False):
    """
    If path is specified, save data to path if not yet exists.
    """
    protocol, uri = uri.split('://')
    if protocol == 'omero':
        username, uri = uri.split('@')
        host, uri = uri.split(':')
        port, uri = uri.split('/')
        from openalea.oalab.gui.utils import password
        password = password()
        from omero.gateway import BlitzGateway
        conn = BlitzGateway(username, password, host=host, port=port)
        if conn.connect():
            img = conn.getObject("Image", uri)
            from tissuelab.omero.utils import image_wrapper_to_ndarray
            matrix = image_wrapper_to_ndarray(img)
            return matrix
