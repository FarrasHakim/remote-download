### Struktur
- Proyek ini terdiri dari 2 bagian. Ada bagian webserver dan agent downloader
- Bagian webserver terletak di folder web/
- Bagian agent downloader terletak di web/service/
  
#### How to run
1. Pastikan python dan rabbitmq terinstall
2. Pastikan rabbitmq sudah menyala
3. Buat sebuah python env dan activate
4. Install requirements dengan `pip install -r requirements`
5. Buka 2 terminal atau cmd
6. Jalankan webserver dengan `python manage.py runserver` di directory web/
7. Jalankan agent downloader dengan `python agentdownloader.py` di directory web/service/

### References when making this project
- https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
- https://www.kite.com/python/answers/how-to-open-a-file-in-a-different-directory-in-python#:~:text=Use%20open()%20to%20open,filename%20from%20the%20current%20directory.
- https://stackoverflow.com/questions/29324037/convert-bytesio-into-file
- https://stackoverflow.com/questions/41106599/python-3-5-urllib-request-urlopen-progress-bar-available
