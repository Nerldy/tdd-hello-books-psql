from app import app
import os
if __name__ == '__main__':
	port = os.getenv('PORT')
	app.run('127.0.0.1', port=int(port))
