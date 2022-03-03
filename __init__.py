# -*- coding: utf-8 -*-
"""
/***************************************************************************
 testadalotes
                                 A QGIS plugin
 Gerar testada de lotes
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-03-01
        copyright            : (C) 2022 by Antônio Teles / Gloria Santos
        email                : antoniot.leandro@gmaill.com/mdgss.gloria@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load testadalotes class from file testadalotes.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .testadalotes import testadalotes
    return testadalotes(iface)
