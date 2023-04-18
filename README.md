<p align=center>
<img src="https://avatars.mds.yandex.net/i?id=81935914ce98f249e1c3b5b6981990e23160f730-9211239-images-thumbs&n=13">
</p>
<p align=center>
<img src="https://img.shields.io/badge/Aiogram-2.25.1-blue?style=for-the-badge&logo=Telegram">
<img src="https://img.shields.io/badge/-Python-029deb?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/-Docker-blue?style=for-the-badge&logo=docker">
<img src="https://img.shields.io/badge/-PostgreSQL-0aa197?style=for-the-badge&logo=PostgreSQL">
</p>

# О боте
<blockquote>Бот-парсер по поиску работы на hh.ru</blockquote>
<details>
<summary>
Что может бот
</summary>
<ul>
<li>Уведомлять новыми вакансиями со следующего дня исходя из настроенных критерий</li>
<li>Сохраняет теущие настройки фильтрации, если устанавливаются новые, то старые удаляются</li>
<li>Присылает вакансии начиная с актуальных с задержкой в 5 секунд</li>
</ul>
</details>

## Запуск при помощи Docker
<ol>
<li>Клонировать этот репозиторий -
<code>git clone https://github.com/BgPyt/aiogram-bot.git</code></li>
<li>В env файле поместить свои параметры для запука</li>
<li>Создание образов и запуск контейнеров <code>docker-compose up -d</code></li>
</ol>
<blockquote>P.S при первичном запуске создаст необходимые таблицы в бд</blockquote>

## Инструкция пользования веб-интерфейсом для postgres (PGADMIN)
Открыть бразурер и введите IP-адрес сервера <code>localhost:8080</code>
<p> Зарегистрировать сервер, где нужно указать имя и пароль пользавателя, которые вы ввели в env файле<p>А так же хост и порт сервера (Имя хоста=db, Порт=5432)
