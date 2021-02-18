CREATE TABLE billboard_charts(
id int(11) PRIMARY KEY AUTO_INCREMENT,
name varchar(255),
year int(11),
date DATE,
is_year_end tinyint
);

CREATE TABLE billboard_chart_artists_producer(
id int(11) PRIMARY KEY AUTO_INCREMENT,
artist varchar(255),
chart_rank INT(11),
chart_id int,
image varchar(255)
);

CREATE TABLE billboard_chart_song_album(
id int(11) PRIMARY KEY AUTO_INCREMENT,
song_album varchar(255),
artist varchar(255),
peak_Pos INT(11),
last_Pos INT(11),
weeks int(11),
isNew tinyInt,
chart_rank INT(11),
chart_id int,
image varchar(255)
);