# AcademyYandex
Предыстория: чтобы немного скрасить жизнь людей на самоизоляции, вы решаете открыть
интернет-магазин по доставке конфет "Сласти от всех напастей".
Ваша задача — разработать на python REST API сервис, который позволит нанимать курьеров на работу,
принимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.

Сервер развернут на машине http://84.201.132.114. С портом 8080. Под управлением веб-сервера Apache2. 

____

# Инструкция по установке

1. Установка и включение mod_wsgi 

    a. Сначала устанавливаем mod_wsgi:

    ```shell
    sudo apt-get install libapache2-mod-wsgi python-dev
    ```
    b. Потом запускаем mod_wsgi: 
    
    ```shell
    sudo a2enmod wsgi
    ```
2. Клонируем репозиторий на машину
    
    a. В ```/var/www``` создаем папку ```AcademyYandex``` с нашим сервером.
    b. Клонируем репозиторий в эту папку 
    
    ```shell
    sudo git clone https://github.com/dimkashelk/AcademyYandex.git
    ```
3. Устанавливаем необходимые пакеты
    
    ```shell
    sudo pip3 install -r requirements.txt
    ```
4. Настройка виртуального хоста

    a. Редактируем файл конфигурации 
    
    ```shell
    sudo nano /etc/apache2/sites-available/AcademyYandex.conf
    ```
    
    В него вставляем
    ```commandline
    <VirtualHost *:8080>
    ServerName 84.201.132.114
    ServerAdmin entrant@84.201.132.114
    WSGIScriptAlias / /var/www/AcademyYandex/academyyandex.wsgi
    <Directory /var/www/AcademyYandex/AcademyYandex/>
    Order allow,deny
    Allow from all
    </Directory>
    Alias /static /var/www/AcademyYandex/AcademyYandex/static
    <Directory /var/www/AcademyYandex/AcademyYandex/static/>
    Order allow,deny
    Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    ```
    
    b. Включаем виртуальный хост
    
    ```shell
    sudo a2ensite AcademyYandex
    ```
    
5. Создание файла .wsgi 
    
    Для обслуживания приложений Flask сервер Apache использует файл .wsgi. перейдите в каталог приложения (```/var/www/AcademyYandex```) и создайте файл academyyandex.wsgi:
    
    ```shell
    cd /var/www/AcademyYandex
    sudo nano academyyandex.wsgi
    ```
    
    Внесите в файл следующий код:
    
    ```python3
    #!/usr/bin/python
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr)
    sys.path.insert(0,"/var/www/AcademyYandex/")
    from AcademyYandex.main import app as application
    application.secret_key = 'Add your secret key'
    ```
    
    На данном этапе структура каталогов имеет такой вид:
    
    ```
    |--------AcademyYandex
    |----------------AcademyYandex
    |-----------------------data
    |------------------------------__all_models.py
    |------------------------------couriers.py
    |------------------------------db_session.py
    |------------------------------orders.py
    |-----------------------db
    |------------------------------db.db
    |-----------------------session.py
    |-----------------------requirements.txt
    |-----------------------__init__.py
    |----------------academyyandex.wsgi
    ```
 
6. Перезапуск Apache

    ```shell
    sudo service apache2 restart
    ```

7. Меняем порты для сервера

    По умолчанию apache2 прослушивает только 80 (для http) и 442 (для https) порты. Поэтому нам надо подключить порт 8080. Для этого редактируем файл ```/etc/apache2/ports.conf``` и добавляем строчку ```Listen 8080```. Изменяем в файле ```/etc/apache2/sites-enabled/000-default.conf``` порт ```80``` на ```8080```.
    Перезагружаем apache2.
    ```shell
    sudo systemctl restart apache2
    ```

8. Устанавливаем mysql 

    Сначала установим необходимые пакеты:
    ```shell
    sudo apt install mysql-server mysql-client
    ```   

9. Настройка mysql
   
    Перед тем как вы сможете полноценно использовать только что установленную базу данных, необходимо выполнить ее первоначальную настройку
    ```shell
    sudo mysql_secure_installation
    ```   
    Везде можно проставить y.

    Создаем таблицу с базой данных
    ```mysql
    CREATE DATABASE db;
    ```
   
    Далее создадим пользователя:

    ```mysql
    CREATE USER entrant@'localhost' IDENTIFIED BY 'qwerty123';
    ```
   
    Добавляем прав для нового пользователя.
    
    ```mysql
    GRANT ALL PRIVILEGES ON db . * TO 'entrant'@'localhost';
    ```

    Сохраняем права.
    
    ```mysql
    FLUSH PRIVILEGES;
    ```

Сервер развернут и готов к использованию. 

____


