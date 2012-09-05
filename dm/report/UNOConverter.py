#!/usr/bin/env python
#
# PyODConverter (Python OpenDocument Converter) v1.0.0 - 2008-05-05
#
# This script converts a document from one office format to another by
# connecting to an OpenOffice.org instance via Python-UNO bridge.
#
# Copyright (C) 2008 Mirko Nasato <mirko@artofsolving.com>
#                    Matthew Holloway <matthew@holloway.co.nz>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl-2.1.html
# - or any later version.
#

DEFAULT_OPENOFFICE_PORT = 2002
import os
from os.path import abspath
from os.path import isfile
from os.path import splitext
import sys
import uno
from StringIO import StringIO
import time
import tempfile

import unohelper
from com.sun.star.beans import PropertyValue
from com.sun.star.task import ErrorCodeIOException
from com.sun.star.uno import Exception as UnoException
from com.sun.star.connection import NoConnectException
from com.sun.star.io import XOutputStream
FAMILY_TEXT = "Text"

FILTER_MAP = {
    "pdf": "writer_pdf_Export",
    "html": "HTML (StarWriter)",
    "odt": "writer8" ,
    "doc": "MS Word 97" ,
    "rtf": "Rich Text Format" ,
    "txt": "Text" ,
}
class OutputStream( unohelper.Base, XOutputStream ):
	""" Minimal Implementation of XOutputStream """
	def __init__(self, debug=True):
		self.debug = debug
		self.data = StringIO()
		self.position = 0
		if self.debug:
			sys.stderr.write("__init__ OutputStreamWrapper.\n")

	def writeBytes(self, bytes):
		if self.debug:
			sys.stderr.write("writeBytes %i bytes.\n" % len(bytes.value))
		self.data.write(bytes.value)
		self.position += len(bytes.value)

	def close(self):
		if self.debug:
			sys.stderr.write("Closing output. %i bytes written.\n" % self.position)
		self.data.close()

	def flush(self):
		if self.debug:
			sys.stderr.write("Flushing output.\n")
		pass

class DocumentConverter:
	def __init__(self, port=DEFAULT_OPENOFFICE_PORT):
		connection = "socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % (port)
		self.localContext = uno.getComponentContext()
		self.ServiceManager = self.localContext.ServiceManager
		resolver = self.localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", self.localContext)
		self.desktop = False
		context = False
		try:
			context = resolver.resolve("uno:%s" % connection)
		except Exception,e:
			for bin in ('soffice.bin', 'soffice', ):
				try:
					oopid = os.spawnvp(os.P_NOWAIT, bin, [bin, "-nologo", "-nodefault", "-accept=%s" % connection]);
					time.sleep(1)
					context = resolver.resolve("uno:%s" % connection)
					break
				except Exception, e:
					continue
		if context :
			self.desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
            
	def convertByStream(self, stdinBytes, outputExt='pdf'):
		inputStream = self.ServiceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream", self.localContext)
		inputStream.initialize((uno.ByteSequence(stdinBytes),))
		
		document = self.desktop.loadComponentFromURL('private:stream' , "_blank", 0,  self._toProperties(Hidden=True,InputStream=inputStream) )	
			
		if not document:
			raise Exception, "Error making document"
		try:
			document.refresh()
		except AttributeError:
			pass

		filterName = FILTER_MAP[outputExt]
		outputStream = OutputStream(False)

		try:
			outputprops = self._toProperties(
							OutputStream = outputStream,
							FilterName = filterName,
							Overwrite = True)
			document.storeToURL("private:stream", outputprops)
		finally:
			document.close(True)

		data= outputStream.data.getvalue()
		outputStream.close()
		return data
	
	def storeByPath(self, stdinBytes, outputExt='pdf'):
		inputStream = self.ServiceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream", self.localContext)
		inputStream.initialize((uno.ByteSequence(stdinBytes),))

		document = self.desktop.loadComponentFromURL('private:stream' , "_blank", 0,  self._toProperties(Hidden=True,InputStream=inputStream) )	
			
		if not document:
			raise Exception, "Error making document"
		try:
			document.refresh()
		except AttributeError:
			pass

		filterName = FILTER_MAP[outputExt]
		outputFile = tempfile.mktemp(suffix='.%s'%outputExt)
		outputUrl = self._toFileUrl(outputFile)

		try:
			document.storeToURL(outputUrl, self._toProperties(FilterName=FILTER_MAP[outputExt],Overwrite=True))
		finally:
			document.close(True)

		data= open(outputFile,"rb").read()
		return data


	def convertByPath(self, inputFile, outputFile, outputExt='pdf'):
		inputUrl = self._toFileUrl(inputFile)
		outputUrl = self._toFileUrl(outputFile)
		document = self.desktop.loadComponentFromURL(inputUrl, "_blank", 0, self._toProperties(Hidden=True))

		if not document:
			raise Exception, "Error making document"

		try:
			document.refresh()
		except AttributeError:
			pass

		try:
			document.storeToURL(outputUrl, self._toProperties(FilterName=FILTER_MAP[outputExt]))
		finally:
			document.close(True)

	def _toFileUrl(self, path):
		return uno.systemPathToFileUrl(abspath(path))

	def _toProperties(self, **args):
		props = []
		for key in args:
			prop = PropertyValue()
			prop.Name = key
			prop.Value = args[key]
			props.append(prop)
		return tuple(props)

if __name__ == "__main__":
	try:
		if len(sys.argv) == 2 and sys.argv[1] == '--stream':
			stdinBytes = sys.stdin.read()
			converter = DocumentConverter()
			openDocumentBytes = converter.convertByStream(stdinBytes ,outputExt)
			sys.stdout.write(openDocumentBytes)
			sys.stderr.write("(Success)\n")
			sys.exit(0)
		elif len(sys.argv) == 3:
			converter = DocumentConverter()
			if not isfile(sys.argv[1]):
				sys.stderr.write("No such input file: %s\n" % sys.argv[1])
				sys.exit(1)
			converter.convertByPath(sys.argv[1], sys.argv[2])
		else:
			helpText = "USAGE: " + sys.argv[0] + " <input-path> <output-path>\n"
			helpText += "USAGE: " + sys.argv[0] + " --stream  (accepts binary document on stdin and outputs on stdout)\n"
			sys.stderr.write(helpText)
			sys.exit(2)
	except Exception, exception:
		sys.stderr.write("Error: %s" % exception)
		sys.exit(1)


