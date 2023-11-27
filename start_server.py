#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.validator.file_server import FileServer

file_server = FileServer(file_directory=".", server_port=8000)
file_server.start_server()
